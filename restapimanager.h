#ifndef RESTAPIMANAGER_H
#define RESTAPIMANAGER_H

#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>

class RestAPIManager : public QObject
{
    Q_OBJECT
public:
    explicit RestAPIManager(QObject *parent = nullptr);

    void RequestAssets();

    void fetchData(const QUrl &url);

signals:
    void dataFetched(const QByteArray &data);
    void errorOccurred(const QString &errorString);

private slots:
    void onNetworkReply(QNetworkReply *reply);

private:
    QNetworkAccessManager *m_networkAccessManager;
};

#endif // RESTAPIMANAGER_H
