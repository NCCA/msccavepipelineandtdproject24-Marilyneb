#include "modelbrowser.h"
#include "./ui_modelbrowser.h"
#include <QFileDialog>
#include "restapimanager.h"
#include <QDebug>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonValue>
#include <QUrl>
#include <QVBoxLayout>
#include <emscripten.h>
#include <QDockWidget>
#include <QJsonArray>
#include <QFormLayout>
#include <QLineEdit>
#include <QPushButton>
#include <QHttpMultiPart>
#include <QNetworkAccessManager>
#include <QNetworkCookieJar>
#include <QNetworkCookie>
#include <QtQuick/QtQuick>

ModelBrowser::ModelBrowser(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::ModelBrowser)
    , networkAccessManager(new QNetworkAccessManager(this))
{
    ui->setupUi(this);
    m_restAPIManager = new RestAPIManager(networkAccessManager, this);

    fetchAssets();


    QWidget *formWidget = new QWidget(this);
    QFormLayout *formLayout = new QFormLayout(formWidget);



    QLineEdit *usernameLineEdit = new QLineEdit(this);
    QLineEdit *passwordLineEdit = new QLineEdit(this);
    passwordLineEdit->setEchoMode(QLineEdit::Password);

    QPushButton *loginButton = new QPushButton("Login", this);
    QPushButton *registerButton = new QPushButton("Register", this);

    formLayout->addRow("Username:", usernameLineEdit);
    formLayout->addRow("Password:", passwordLineEdit);
    formLayout->addRow(loginButton);
    formLayout->addRow(registerButton);


    QDockWidget *dockWidget = new QDockWidget("Login / Register", this);
    dockWidget->setWidget(formWidget);

    addDockWidget(Qt::RightDockWidgetArea, dockWidget);

    connect(loginButton, &QPushButton::clicked, this, [=]() {
        m_restAPIManager->login(usernameLineEdit->text(), passwordLineEdit->text());
    });

    connect(registerButton, &QPushButton::clicked, this, [=]() {
        m_restAPIManager->registerUser(usernameLineEdit->text(), passwordLineEdit->text());
    });

    connect(ui->uploadButton, &QPushButton::clicked, this, &ModelBrowser::on_uploadButton_clicked);


}

void uploadFile(const QString &fileName, const QByteArray &fileContent) {

    if (fileName.isEmpty())
        return;

    QString fileContentStr = QString::fromUtf8(fileContent);
    QString fileNameOnly = QFileInfo(fileName).fileName();

    EM_ASM({
        var fileName = UTF8ToString($0);
        var fileContent = UTF8ToString($1);

        var apiUrl = 'http://127.0.0.1:30001/upload';
        var mimeType = 'application/octet-stream';

        var blobData = new Blob([fileContent], { type: mimeType });

        var formData = new FormData();
        formData.append('file', blobData, fileName);

        var is3dModel = fileName.includes(".obj") || fileName.includes(".stl");

        var re = /(?:\.([^.]+))?$/;

        var fileExtension = re.exec(fileName)[1];

        let tagsArray = [];

        if(is3dModel)
        {
            tagsArray.push("3DModel");
        }

        tagsArray.push(fileExtension);

        formData.append('tags', tagsArray);

        fetch(apiUrl, {
            method: 'POST',
            body: formData,
            credentials: 'include' // Ensure cookies are sent with the request
        })
            .then(function(response) {
                if (response.ok) {
                    console.log('File uploaded successfully');
                } else {
                    console.error('File upload failed:', response.status);
                }
            })
            .catch(function(error) {
                console.error('File upload failed:', error);
            });
    }, fileNameOnly.toUtf8().constData(), fileContentStr.toUtf8().constData());


}

void ModelBrowser::on_uploadButton_clicked()
{
    auto fileContentReady = [this](const QString &fileName, const QByteArray &fileContent) {
        uploadFile(fileName, fileContent);
        fetchAssets();
        this->ui->tableWidget->update();
        this->ui->tableWidget->repaint();
        this->repaint();
        qApp->processEvents();
        QTimer::singleShot(1000, this, &ModelBrowser::fetchAssets);
    };

    QFileDialog::getOpenFileContent("3D Model Files (*.obj *.stl)", fileContentReady);

}
ModelBrowser::~ModelBrowser()
{
    delete ui;
}

void ModelBrowser::download()
{
    QString assetName = ui->tableWidget->item(ui->tableWidget->currentRow(), 0)->text();

    QUrl apiUrl("http://127.0.0.1:30001/assets/"+assetName);
    QByteArray apiUrlArray = apiUrl.toString().toUtf8();


EM_ASM({
    var assetUrl = UTF8ToString($0);
    var assetName = UTF8ToString($1);

    fetch(assetUrl).then(response => {
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }

        const contentLength = response.headers.get('content-length');
        if (!contentLength) {
            throw new Error('Content-Length response header unavailable');
        }

        const total = parseInt(contentLength, 10);
        let loaded = 0;

        const reader = response.body.getReader();
        const stream = new ReadableStream({
            start(controller) {
                function push() {
                    reader.read().then(({done, value}) => {
                        if (done) {
                            controller.close();
                            return;
                        }
                        loaded += value.byteLength;
                        const progress = `Progress: ${((loaded / total) * 100).toFixed(2)}%`;
                        console.log(progress);
                        controller.enqueue(value);
                        push();
                    }).catch(error => {
                        console.error('Error reading stream:', error);
                        controller.error(error);
                    });
                }

                push();
            }
        });

        return new Response(stream);
    }).then(response => response.blob())
      .then(blob => {
          var url = window.URL.createObjectURL(blob);
          var a = document.createElement('a');
          a.href = url;
          a.download = assetName;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
      }).catch(error => {
          console.error('Fetch error:', error);
      });
}, apiUrlArray.constData(), assetName.toUtf8().constData());


}


void ModelBrowser::fetchAssets()
{
    QUrl apiUrl("http://127.0.0.1:30001/assets");
    QNetworkRequest request(apiUrl);
    QNetworkAccessManager *networkAccessManager = new QNetworkAccessManager(this);
    QNetworkReply *reply = networkAccessManager->get(request);

    connect(reply, &QNetworkReply::finished, this, [=]() {
        if (reply->error() != QNetworkReply::NoError) {
            // Handle error
            return;
        }

        QByteArray responseBytes = reply->readAll();
        QJsonDocument jsonDoc = QJsonDocument::fromJson(responseBytes);
        QJsonObject jsonObj = jsonDoc.object();
        QJsonArray assetsArray = jsonObj["assets"].toArray();

        updateTable(assetsArray);
    });

}
void ModelBrowser::show3DView(const QString &assetName)
{
    QString url = QString("http://127.0.0.1:30001/view_model/%1").arg(assetName);
    QDesktopServices::openUrl(QUrl(url));
}
void ModelBrowser::searchAssets(const QString &tag)
{
    if(tag == "")
    {
        fetchAssets();
        return;
    }
    QUrl apiUrl("http://127.0.0.1:30001/search/" + tag);
    QNetworkRequest request(apiUrl);
    QNetworkAccessManager *networkAccessManager = new QNetworkAccessManager(this);
    QNetworkReply *reply = networkAccessManager->get(request);

    connect(reply, &QNetworkReply::finished, this, [=]() {
        if (reply->error() != QNetworkReply::NoError) {
            // Handle error
            return;
        }

        QByteArray responseBytes = reply->readAll();
        QJsonDocument jsonDoc = QJsonDocument::fromJson(responseBytes);
        QJsonObject jsonObj = jsonDoc.object();
        QJsonArray assetsArray = jsonObj["assets"].toArray();


        updateTable(assetsArray);  // Update the table with the search results

    });
}
void ModelBrowser::updateTable(const QJsonArray &assetsArray)
{
    ui->tableWidget->setRowCount(assetsArray.size());  // Set the number of rows in the table
    ui->tableWidget->setColumnCount(4);  // Set the number of columns in the table

    QStringList headers = {"Name", "Tags", "View", "Download"};
    ui->tableWidget->setHorizontalHeaderLabels(headers);  // Set the header labels
    ui->tableWidget->setEditTriggers(QAbstractItemView::NoEditTriggers);

    for (int i = 0; i < assetsArray.size(); ++i) {
        QJsonObject assetObj = assetsArray[i].toObject();
        QString name = assetObj["name"].toString();
        QJsonArray tagsArray = assetObj["tags"].toArray();

        QStringList tags;
        for (int j = 0; j < tagsArray.size(); ++j) {
            tags.append(tagsArray[j].toString());
        }

        // Add the name and tags to the table
        ui->tableWidget->setItem(i, 0, new QTableWidgetItem(name));
        ui->tableWidget->setItem(i, 1, new QTableWidgetItem(tags.join(", ")));

        QPushButton *viewButton = new QPushButton("View");
        ui->tableWidget->setCellWidget(i, 2, viewButton);
        connect(viewButton, &QPushButton::clicked, this, [=]() {
            QString assetName = name;
            show3DView(assetName);
        });

        QPushButton *downloadButton = new QPushButton("Download");
        ui->tableWidget->setCellWidget(i, 3, downloadButton);
        connect(downloadButton, &QPushButton::clicked, this, &ModelBrowser::download);
    }

    ui->tableWidget->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    ui->tableWidget->verticalHeader()->setSectionResizeMode(QHeaderView::Stretch);
}

void ModelBrowser::on_lineEdit_2_textChanged(const QString &arg1)
{
    searchAssets(ui->lineEdit_2->text());
}

