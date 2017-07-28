Changes 20-02-2017
------------------------
- Function "sample" is fixed (now sampling with the correct parameters)
- Added an extension to 2.5, "Regularisation"
- Changed the mainRBM.py file in various ways to make the learning better
    - In an epoch, go over all users in a random order

Changes 21-02-2017
------------------------
- Explain how to create final prediction csv in project
- Add new validation.csv set, remove splitDataset from projectLib.py, instead get validation dataset by calling lib.getValidationData()
- Changes in rbm.py:
    - Add new predictForUser function
    - Update getPredictedDistribution function, remove argument "q" (unnecessary and confusing)
    - Give implementation of getV to avoid confusion
- Changes in mainRBM.py file:
    - posprods and negprods are updated in every pass, and not reset to zero
    - Provide example code to save predicted ratings

Changes 27-02-2017
-------------------------
- Remove first week of submissions, 4 tries only on the test set

Changes 28-02-2017
-------------------------
- Minor changes in project description, more details in question 2.4 and for momentum method.
