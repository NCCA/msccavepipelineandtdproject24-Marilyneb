#include "restapimanager.h"


RestAPIManager::RestAPIManager(QObject *parent)
    : QObject(parent), m_networkAccessManager(new QNetworkAccessManager(this))
{
    connect(m_networkAccessManager, &QNetworkAccessManager::finished,
            this, &RestAPIManager::onNetworkReply);
}

void RestAPIManager::RequestAssets()
{
    fetchData(QUrl("http://127.0.0.1:5000/assets"));
}

void RestAPIManager::fetchData(const QUrl &url)
{
    QNetworkRequest request(url);
    m_networkAccessManager->get(request);
}

void RestAPIManager::onNetworkReply(QNetworkReply *reply)
{
    if (reply->error() == QNetworkReply::NoError) {
        QByteArray data = reply->readAll();
        qDebug() << "Received data:" << data;
        emit dataFetched(data);
    } else {
        emit errorOccurred(reply->errorString());
    }
    reply->deleteLater();
}
