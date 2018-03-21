import pandas as pd

from mentat import ZDataFrame
from mentat.evaluator import ClassificationEvaluator
from mentat.model import DNN
from mentat.pipeline import Pipeline
from mentat.preprocessor import StandardScaler
from mentat.trainer import MultiModelTrainer

# load and construct the data frame
df = pd.read_csv("../data/bird.csv")
data = ZDataFrame(df, response_column="type", ignores=["id"], response_encode="multiclass").impute("mean")

# split the data into train(and test) dataset and dataset to be predicted
train_and_test, to_be_predicted = data.split(.7)

# construct 3 models(DNN) with dirfferent hyperparameters(size of hidden layer and max epochs here)
dnns = {
    "dnn_1": DNN(len(data.feature_cols), [2, len(data.category)], ["relu", "identity"], softmax=True, max_epochs=2),
    "dnn_2": DNN(len(data.feature_cols), [20, len(data.category)], ["relu", "identity"], softmax=True, max_epochs=20),
    "dnn_3": DNN(len(data.feature_cols), [60, len(data.category)], ["relu", "identity"], softmax=True, max_epochs=30)
}

# construct a pipeline contains a standardizer and a multi-model trainner(train 3 DNN parallelly)
pipeline = Pipeline(
    {
        "preprocessor": StandardScaler(),
        "trainer": MultiModelTrainer(dnns, train_fraction=.7, evaluator=ClassificationEvaluator(),
                                     metric="accuracy")
    }
)

# fit the pipeline
pipeline.fit(train_and_test)

# the accuracies of 3 DNN
for name, accuracy in pipeline.get_operator("trainer").metrics.items():
    print("model: {:s}  accuracy: {:.6f}".format(name, accuracy))

# metrics of the chosen(best) DNN
eva = pipeline.get_operator("trainer").get_evaluator()
print(eva.confusion_matrix())
print(eva.report())
print(eva.accuracy())

#  use pipeline to predict
predict = pipeline.evaluate(to_be_predicted)

# ZDataFrame is callable, return the data(pandas DataFrame) it contains
print(predict().head(5))
