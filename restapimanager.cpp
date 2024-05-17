#include "restapimanager.h"
#include <QUrlQuery>
#include <QFile>
#include <QDebug>
#include <QFileInfo>
#include <QHttpMultiPart>
#include <QNetworkCookieJar>
#include <QNetworkCookie>
#include <emscripten.h>


RestAPIManager::RestAPIManager(QObject *parent)
    : QObject(parent), m_networkAccessManager(new QNetworkAccessManager(this))
{
    connect(m_networkAccessManager, &QNetworkAccessManager::finished,
            this, &RestAPIManager::onNetworkReply);
    m_networkAccessManager->setCookieJar(new QNetworkCookieJar());

    m_cookieUrl = QUrl("http://localhost:30001/upload");
    //get cookie
    m_networkAccessManager->get(QNetworkRequest(m_cookieUrl));
}
RestAPIManager::RestAPIManager(QNetworkAccessManager *networkAccessManager, QObject *parent)
    : QObject(parent), m_networkAccessManager(networkAccessManager)
{
    connect(m_networkAccessManager, &QNetworkAccessManager::finished,
            this, &RestAPIManager::onNetworkReply);
}
void RestAPIManager::RequestAssets()
{
    fetchData(QUrl("http://127.0.0.1:30001/assets"));
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


void RestAPIManager::login(const QString &username, const QString &password)
{
    postData(QUrl("http://127.0.0.1:30001/login"), username, password);
}

void RestAPIManager::registerUser(const QString &username, const QString &password)
{
    postData(QUrl("http://127.0.0.1:30001/register"), username, password);
}

void RestAPIManager::postData(const QUrl &url, const QString &username, const QString &password)
{
    QString postData = QString("username=%1&password=%2").arg(username, password);

    EM_ASM({
        var url = UTF8ToString($0);
        var postData = UTF8ToString($1);

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: postData,
            credentials: 'include' // Ensure cookies are sent with the request
        })
            .then(function(response) {
                if (response.ok) {
                    console.log('Success:', response.statusText);
                    // You can access response body using response.text(), response.json(), etc.
                } else {
                    console.error('Request failed with status:', response.status);
                }
            })
            .catch(function(error) {
                console.error('Request failed:', error);
            });
    }, url.toString().toUtf8().constData(), postData.toUtf8().constData());
}
