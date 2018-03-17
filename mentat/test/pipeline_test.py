from mentat import ZDataFrame
from mentat.preprocessor import StandardScaler
from mentat.model import DNN
from mentat.trainer import TrivialTrainer
from mentat.pipeline import Pipeline
import pandas as pd
import numpy as np

# load and construct the data frame
bird = pd.read_csv("../data/bird.csv")
data = ZDataFrame(bird, response_column="type", ignores=["id"], response_encode="multiclass")
data.impute()

# keep a test set out
train, test = data.split(0.6)

# deep neural network
dnn = DNN(
    input_shape=len(data.feature_cols),
    shape=[20, len(data.category)],
    activations=["sigmoid", "identity"],
    eta=1.0,
    threshold=1e-5,
    softmax=True,
    max_epochs=50,
    regularization=0.0001,
    minibatch_size=10,
    momentum=0.9,
    decay_power=0.2,
    verbose=True
)

# preprocessor: standard scaler
preprocessor = StandardScaler()

# trivial trainer
trainer = TrivialTrainer(dnn, train_fraction=0.7)

# pipeline
pipeline = Pipeline()
pipeline.add_operator(preprocessor)
pipeline.add_operator(trainer)

# train
pipeline.fit(train)

# predict
result = pipeline.evaluate(test)

# accuracy score (evaluation module is not finished)
accuracy = (result.data["predict_category"] == result.data["type"]).astype(np.int).sum() / len(result.data)
print("accuracy: {:.3f}".format(accuracy))