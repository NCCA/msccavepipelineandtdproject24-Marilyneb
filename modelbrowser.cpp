#include "modelbrowser.h"
#include "./ui_modelbrowser.h"

#include "restapimanager.h"
#include <QDebug>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonValue>
#include <QFile>
#include <QUrl>
#include <QVBoxLayout>
#include <emscripten.h>



ModelBrowser::ModelBrowser(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::ModelBrowser)
{

    m_restAPIManager = new RestAPIManager(this);

    ui->setupUi(this);
}

ModelBrowser::~ModelBrowser()
{
    delete ui;
}

void ModelBrowser::on_pushButton_6_clicked()
{
    QObject::connect(m_restAPIManager, &RestAPIManager::dataFetched, [=](const QByteArray &data) {
         QFile file("downloaded_data.json");
         if (file.open(QIODevice::WriteOnly)) {
             file.write(data);
             file.close();
             qDebug() << "JSON file downloaded successfully.";

             EM_ASM({
                 var data = new Uint8Array(Module.HEAPU8.subarray($0, $0 + $1));
                 var blob = new Blob([data], { type: "application/json" });
                 var url = window.URL.createObjectURL(blob);
                 var a = document.createElement("a");
                 a.href = url;
                 a.download = "downloaded_data_.json";
                 document.body.appendChild(a);
                 a.click();
                 document.body.removeChild(a);
                 window.URL.revokeObjectURL(url);


             }, data.constData(), data.size());
         } else {
             qDebug() << "Failed to write JSON file.";
         }
    });

    QObject::connect(m_restAPIManager, &RestAPIManager::errorOccurred, [=](const QString &errorString) {
        qDebug() << "Error occurred HELLO WORLD :" << errorString;
    });

    QUrl apiUrl("http://127.0.0.1:5000/assets");
    m_restAPIManager->fetchData(apiUrl);
}



