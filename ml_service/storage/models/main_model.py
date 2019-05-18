#!/usr/bin/env python
# coding: utf-8

import xgboost as xgb
from sklearn.metrics import accuracy_score, recall_score, precision_score, log_loss, roc_auc_score


class Model:

    def __init__(self):
        self.model = xgb.XGBClassifier()

    def load(self, res_path):
        self.model.load_model(res_path)

    def predict(self, data):
        y_test = data[:, -1]
        y_hat = self.model.predict(data[:, :-1])
        y_hat_proba = self.model.predict_proba(data[:, :-1])

        accuracy = accuracy_score(y_pred=y_hat, y_true=y_test)
        precision = precision_score(y_pred=y_hat, y_true=y_test)
        recall = recall_score(y_pred=y_hat, y_true=y_test)
        logloss = log_loss(y_pred=y_hat_proba, y_true=y_test)
        roc_auc = roc_auc_score(y_pred=y_hat_proba, y_true=y_test)

        result = {'accuracy': accuracy, 'precision': precision,
                  'recall': recall, 'log_loss': logloss,
                  'roc_auc':roc_auc}
        return result