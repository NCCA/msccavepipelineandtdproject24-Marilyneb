#ifndef RESTAPIMANAGER_H
#define RESTAPIMANAGER_H

#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonObject>

class RestAPIManager : public QObject
{
    Q_OBJECT
public:
    explicit RestAPIManager(QObject *parent = nullptr);
    explicit RestAPIManager(QNetworkAccessManager *networkAccessManager, QObject *parent = nullptr);


    void RequestAssets();
    void fetchData(const QUrl &url);

    void login(const QString &username, const QString &password);
    void registerUser(const QString &username, const QString &password);

    void postData(const QUrl &url, const QString &username, const QString &password);

    void uploadFile(const QString &filePath);


signals:
    void dataFetched(const QByteArray &data);
    void errorOccurred(const QString &errorString);


private slots:
    void onNetworkReply(QNetworkReply *reply);

private:
    QNetworkAccessManager *m_networkAccessManager;

    QNetworkCookieJar *m_cookieJar;

    QUrl m_cookieUrl;
};

#endif // RESTAPIMANAGER_H
