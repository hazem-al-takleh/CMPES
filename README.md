# CMPES

Cognitive Memory Preservation and Enhancement System is a software and hardware system that helps with the pre-diagnosis, diagnosis, and post-diagnosis problems of dementia.

CMPES has 2 interfaces:
1. A software Mobile Application interface
2. A hardware Embedded System interface

CMPES has 3 users that are listed as follows:
1. Potential Dementia Patient
2. Caregiver
3. Dementia Patient

CMPES helps the Potential Dementia Patient in the pre-diagnosis phase by predicting how much he/she is likely to be diagnosed with dementia in the next 5 years based on the patient's lifestyle.
This feature is backed by a predictive machine learning algorithm which is a proportional hazards prediction model (Cox regression). The Potential Dementia Patient interacts with the system through the mobile application where the answers to the lifestyle questionnaire are gathered and sent to the ML model to be processed.

CMPES helps also helps the Potential Dementia Patient by diagnosing his mental state by the MMSE cognitive test in our mobile application.
The answers to the MMSE are gathered and sent to the system to be processed, the patient's mental state is classified based on the score in the MMSE.

Finally, CMPES's hardware interface helps the caregiver of dementia patients with their most important two tasks that are:
1. Wandering prevention: The system notifies the caregiver if the patient is inside his house or not.
2. Auditory notification: The system notifies the patient of tasks sent by the caregiver at their time.
