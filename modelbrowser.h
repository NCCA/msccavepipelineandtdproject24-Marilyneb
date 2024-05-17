#ifndef MODELBROWSER_H
#define MODELBROWSER_H

#include <QMainWindow>
#include <QNetworkAccessManager>
#include <QListWidget>

class RestAPIManager;

QT_BEGIN_NAMESPACE
namespace Ui {
class ModelBrowser;
}
QT_END_NAMESPACE

class ModelBrowser : public QMainWindow
{
    Q_OBJECT

public:
    ModelBrowser(QWidget *parent = nullptr);
    ~ModelBrowser();

    void fetchAssets();
    void on_tableWidget_cellClicked(int row, int column);



private slots:
    void download();
    void on_uploadButton_clicked();
    void show3DView(const QString &assetName);
    void searchAssets(const QString &tag);
    void updateTable(const QJsonArray &assetsArray);

    void on_lineEdit_2_textChanged(const QString &arg1);

private:
    Ui::ModelBrowser *ui;
    QNetworkAccessManager *networkAccessManager;
    RestAPIManager *m_restAPIManager;
    QString m_authToken;
    QListWidget *listWidget;
    QLineEdit *tagsLineEdit;
};
#endif // MODELBROWSER_H
