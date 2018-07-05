import joblib
import numpy as np

class HousingServe(object):
    def __init__(self, model_file='housing.dat'):
        """Load the housing model using joblib."""
        self.model = joblib.load(model_file)

    def predict(self, X):
        """Predict using the model for given ndarray."""
        return self.model.predict(data=X)

    def sample_test(self):
        """Generate a random sample feature."""
        return np.ndarray([1, 37])

if __name__=='__main__':
    serve = HousingServe()
    print(serve.predict(serve.sample_test()))
