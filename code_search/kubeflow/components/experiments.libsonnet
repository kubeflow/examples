// Data for various experiments.
// Paths are deliberately hard coded so they get versioned and checked into source control.
{
  "demo-trainer-11-07-dist-sync-gpu": {
    name: "demo-trainer-11-07-dist-sync-gpu",
    outputDir: "gs://code-search-demo/models/20181107-dist-sync-gpu",
    train_steps: 200000,
    eval_steps: 100,
    hparams_set: "transformer_base",
    project: "code-search-demo",    
    modelDir: "gs://code-search-demo/models/20181107-dist-sync-gpu/export/1541712907/",    
    problem: "kf_github_function_docstring",
    model: "kf_similarity_transformer",
  },
}
