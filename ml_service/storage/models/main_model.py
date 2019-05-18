#!/usr/bin/env python
# coding: utf-8

import xgboost as xgb
from sklearn.metrics import accuracy_score, recall_score, precision_score, log_loss, roc_auc_score


class Model:

    def load(self, res_path):
        self.model = xgb.load_model(res_path)

    def predict(self, data):
        y_test = data[:, -1]
        y_hat = self.model.predict(data[:, :-1])
        y_hat_proba = self.model.predict_proba(data[:, :-1])

        accuracy_score(y_pred=y_hat, y_true=y_test)
        precision_score(y_pred=y_hat, y_true=y_test)
        recall_score(y_pred=y_hat, y_true=y_test)
        log_loss(y_pred=y_hat_proba, y_true=y_test)
        roc_auc_score(y_pred=y_hat_proba, y_true=y_test)
