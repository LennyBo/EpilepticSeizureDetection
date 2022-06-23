# EpilepticSeizureDetection

# Dependencies

* Tensorflow 
  * needs Cuda and CDUNN installed on the machine aswell as the binaries added to the PATH of the machine.
  * Installation guide [CUDNN](https://www.tensorflow.org/install/gpu)
* Python dependencies
  * pandas
  * matplotlib
  * tensorflow
  * numpy
  * sklearn

# Usage

1. Edit consts.py
   1. Set DATA_LOC to the dataloction downloaded from [app.seermedical.com](https://app.seermedical.com)
   2. Choose the settings for the run
2. Open TrainUnbalanced.ipynb, Train50-50.ipynb or Train50-50Advanced.ipynb
   1. Run the notebook

This will load the data, train a model and save the results in a .csv file.
Choose the name of the csv file at the bottom of the notebook.



Checkout the [wiki](https://github.com/LennyBo/EpilepticSeizureDetection/wiki) for more information 
