from kfp import dsl
from kfp import kubernetes


@dsl.component(base_image='registry.access.redhat.com/ubi8/python-39', packages_to_install=['kaggle', 'pandas', 'scikit-learn'])
def kaggle_dataset():
    from kaggle.api.kaggle_api_extended import KaggleApi
    kaggle = KaggleApi()
    kaggle.authenticate()
    kaggle.dataset_download_files(dataset='kamilpytlak/personal-key-indicators-of-heart-disease',
        path='archive/',
        force=True,
        quiet=False,
        unzip=True
    )
    import pandas as pd
    train = pd.read_csv('archive/2020/heart_2020_cleaned.csv')
    numeric_features=['BMI', 'PhysicalHealth', 'MentalHealth', 'SleepTime']
    categorical_features=['HeartDisease', 'Smoking', 'AlcoholDrinking', 'Stroke', 'DiffWalking', 'Sex', 'AgeCategory',
        'Race', 'Diabetic', 'PhysicalActivity', 'GenHealth','Asthma', 'KidneyDisease', 'SkinCancer']

    from sklearn.preprocessing import OrdinalEncoder
    enc = OrdinalEncoder()
    enc.fit(train[categorical_features])
    train[categorical_features] = enc.transform(train[categorical_features])

    y=train['HeartDisease']
    train.drop('HeartDisease',axis=1,inplace=True)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test=train_test_split(train,y,test_size=0.1,random_state=42)
    print(X_train)

    import pickle
    def save_pickle(model, object_file):
        with open(object_file, "wb") as f:
            pickle.dump(model, f)
    save_pickle(X_train, '/data/X_train.pkl')
    save_pickle(X_test, '/data/X_test.pkl')
    save_pickle(y_train, '/data/y_train.pkl')
    save_pickle(y_test,'/data/y_test.pkl')
    import os
    print(os.listdir('/data'))


@dsl.component(base_image='registry.access.redhat.com/ubi8/python-39', packages_to_install=['pandas', 'scikit-learn', 'xgboost'])
def train_model_using(module_name: str, class_name: str):
    print(f'Using model_name: {module_name} {class_name}')
    import os
    print(os.listdir('/data'))
    import pickle
    def save_pickle(model, object_file):
        with open(object_file, "wb") as f:
            pickle.dump(model, f)
    def load_pickle(object_file):
        with open(object_file, "rb") as f:
            return pickle.load(f)
    X_train = load_pickle('/data/X_train.pkl')
    X_test = load_pickle('/data/X_test.pkl')
    y_train = load_pickle('/data/y_train.pkl')
    y_test = load_pickle('/data/y_test.pkl')
    
    from sklearn.metrics import accuracy_score
    from sklearn.metrics import precision_score,recall_score
    from sklearn.metrics import f1_score
    import importlib
    def instantiate_class(module_name, class_name, *args, **kwargs):
        try:
            module = importlib.import_module(module_name)
            class_ = getattr(module, class_name)
            instance = class_(*args, **kwargs)
            return instance
        except ImportError as e:
            print(f"Error importing module {module_name}: {e}")
        except AttributeError as e:
            print(f"Error getting class {class_name} from module {module_name}: {e}")
        except Exception as e:
            print(f"Error instantiating class {class_name} from module {module_name}: {e}")
    m = instantiate_class(module_name, class_name)
    m.fit(X_train, y_train)
    y_pred = m.predict(X_test)

    result = {
        'model': str(m),
        'Accuracy_score': accuracy_score(y_test,y_pred),
        'Precission_score': precision_score(y_test,y_pred),
        'Recall_score': recall_score(y_test,y_pred),
        'F1-score': f1_score(y_test,y_pred),
    }
    print(result)
    save_pickle(result,f'/data/{class_name}_results.pkl') # save result statistics, space-friendly for constrained environments
    

@dsl.component(base_image='registry.access.redhat.com/ubi8/python-39', packages_to_install=['pandas', 'scikit-learn'])
def select_best():
    import os
    import pickle
    def load_pickle(object_file):
        with open(object_file, "rb") as f:
            return pickle.load(f)
    all_files = os.listdir('/data')
    print(all_files)
    result_files = [file for file in all_files if file.endswith("_results.pkl")]
    results = []
    for result_file in result_files:
        file_path = os.path.join('/data', result_file)
        single_result = load_pickle(file_path)
        print(f'Result from file {file_path}: {single_result}')
        results.append(single_result)
    best_result = max(results, key=lambda x: x['Accuracy_score'])
    print("Best result:")
    import json
    print(json.dumps(best_result, indent=2))


@dsl.pipeline
def framingham_cvd_risk_pipeline():
    pvc1 = kubernetes.CreatePVC(
        pvc_name_suffix='-mypipeline-pvc',
        access_modes=['ReadWriteMany'],
        size='500Mi',
        storage_class_name='standard-csi', # might need to change
    )

    dataset_task = kaggle_dataset().set_caching_options(enable_caching=False)
    kubernetes.use_secret_as_env(
        dataset_task,
        secret_name='kaggle-api',
        secret_key_to_env={'KAGGLE_USERNAME': 'KAGGLE_USERNAME', 'KAGGLE_KEY': 'KAGGLE_KEY'})
    kubernetes.mount_pvc(
        dataset_task,
        pvc_name=pvc1.outputs['name'],
        mount_path='/data',
    )

    KNeighborsClassifier_task = train_model_using(module_name="sklearn.neighbors", class_name="KNeighborsClassifier").after(dataset_task).set_caching_options(enable_caching=False)
    kubernetes.mount_pvc(KNeighborsClassifier_task,pvc_name=pvc1.outputs['name'],mount_path='/data')
    LogisticRegression_task = train_model_using(module_name="sklearn.linear_model", class_name="LogisticRegression").after(dataset_task).set_caching_options(enable_caching=False)
    kubernetes.mount_pvc(LogisticRegression_task,pvc_name=pvc1.outputs['name'],mount_path='/data')
    XGBClassifier_task = train_model_using(module_name="xgboost", class_name="XGBClassifier").after(dataset_task).set_caching_options(enable_caching=False)
    kubernetes.mount_pvc(XGBClassifier_task,pvc_name=pvc1.outputs['name'],mount_path='/data')
    ExtraTreesClassifier_task = train_model_using(module_name="sklearn.ensemble", class_name="ExtraTreesClassifier").after(dataset_task).set_caching_options(enable_caching=False)
    kubernetes.mount_pvc(ExtraTreesClassifier_task,pvc_name=pvc1.outputs['name'],mount_path='/data')
    RandomForestClassifier_task = train_model_using(module_name="sklearn.ensemble", class_name="RandomForestClassifier").after(dataset_task).set_caching_options(enable_caching=False)
    kubernetes.mount_pvc(RandomForestClassifier_task,pvc_name=pvc1.outputs['name'],mount_path='/data')
    GradientBoostingClassifier_task = train_model_using(module_name="sklearn.ensemble", class_name="GradientBoostingClassifier").after(dataset_task).set_caching_options(enable_caching=False)
    kubernetes.mount_pvc(GradientBoostingClassifier_task,pvc_name=pvc1.outputs['name'],mount_path='/data')

    select_best_task = select_best().after(KNeighborsClassifier_task,LogisticRegression_task,XGBClassifier_task,ExtraTreesClassifier_task,RandomForestClassifier_task,GradientBoostingClassifier_task).set_caching_options(enable_caching=False)
    kubernetes.mount_pvc(select_best_task,pvc_name=pvc1.outputs['name'],mount_path='/data')

    delete_pvc1 = kubernetes.DeletePVC(pvc_name=pvc1.outputs['name']).after(select_best_task)


if __name__ == '__main__':
    from kfp import compiler
    compiler.Compiler().compile(framingham_cvd_risk_pipeline, __file__+'.yaml')
