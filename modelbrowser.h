#ifndef MODELBROWSER_H
#define MODELBROWSER_H

#include <QMainWindow>

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

private slots:
    void on_pushButton_6_clicked();

private:
    Ui::ModelBrowser *ui;

    RestAPIManager *m_restAPIManager;
};
#endif // MODELBROWSER_H
