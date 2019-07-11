# Dataset

## Upload dataset
Please [download](https://drive.google.com/open?id=1qNNaYguyH_xLfbqnR5ABuYrjblkUEr_z) the dataset and upload it to a Google Cloud Storage location. 

```bash
gsutil cp ner.csv gs://${BUCKET}/data/ner.csv
```

## Dataset description

This example project is using the popular CoNLL 2002 dataset. The csv consists of multiple rows each containing a word with the corresponding tag. Multiple rows are building a single sentence. 

The dataset itself contains different tags
* geo = Geographical Entity 
* org = Organization 
* per = Person 
* gpe = Geopolitical Entity 
* tim = Time indicator 
* art = Artifact 
* eve = Event 
* nat = Natural Phenomenon

Each tag is defined in an IOB format, IOB (short for inside, outside, beginning) is a common tagging format for tagging tokens.

> B - indicates the beginning of a token

> I - indicates the inside of a token

> O - indicates that the token is outside of any entity not annotated

*Next*: [Custom prediction routine](step-4-custom-prediction-routine.md)

*Previous*: [Build the pipeline components](step-2-build-components.md)