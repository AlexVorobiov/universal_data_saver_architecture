from ftplib import FTP
import pandas as pd
from typing import Any

from main import DataSourceAdapter, ConnectionOptions, RawData, DataTransformation, ProcessedData, DataSaver, \
    SynchronizationEngine

FTPDataItem = dict[str, Any]
DjangoModel = Any


class FTPConnectionOptions(ConnectionOptions):
    ftp_server: str
    username: str
    password: str
    remote_path: str
    filename: str

    def __init__(self, _ftp_server: str, _username: str, _password: str, _remote_path: str, _filename: str):
        self.ftp_server = _ftp_server
        self.username = _username
        self.password = _password
        self.remote_path = _remote_path
        self.filename = _filename
        self.ftp = None


class FTPDataSourceAdapter(DataSourceAdapter):
    _ftp: FTP
    _options: FTPConnectionOptions

    def connect(self, options: FTPConnectionOptions) -> None:
        self._ftp = FTP(options.ftp_server)
        self._ftp.login(options.username, options.password)
        self._ftp.cwd(options.remote_path)

    def fetch_data(self) -> RawData:
        with open(self._options.filename, 'wb') as local_file:
            self._ftp.retrbinary('RETR ' + self._options.filename, local_file.write)
        with open(self._options.filename, 'rb') as local_file:
            return local_file.read()


class ExcelDataTransformation(DataTransformation):
    def transform(self, data: RawData) -> ProcessedData[FTPDataItem]:
        # Process Excel data using pandas, assuming the first sheet is the relevant data
        df = pd.read_excel(data)
        result = []
        for index, row in df.iterrows():
            result.append({
                'field1': row['Field1'],
                'field2': row['Field2'],
            })
        return result


class DjangoDataSaverImpl(DataSaver):
    def save(self, data: ProcessedData, target: DjangoModel) -> bool:
        try:
            # Assuming target is a Django model class, and data is a list of dictionaries
            for item in data:
                target.objects.create(**item)
            return True
        except Exception as e:
            # Handle any exceptions that might occur during saving
            return False


class FTPEngine(SynchronizationEngine):

    def synchronize(self, source_adapter: DataSourceAdapter, transformation: DataTransformation,
                    destination_adapter: DataSaver) -> bool:
        # fetch this date from db or config
        ftp_server = "your_ftp_server"
        username = "your_username"
        password = "your_password"
        remote_path = "path_to_xls_file"
        filename = "file.xls"  # Name of the XLS file on the FTP server

        # set you own table, I guess need to think about abstraction for set of models
        target_model = object

        options = FTPConnectionOptions(ftp_server, username, password, remote_path, filename)

        source_adapter.connect(options)
        raw_data = source_adapter.fetch_data()
        processed_data = transformation.transform(raw_data)
        return destination_adapter.save(processed_data, target_model)


# Usage
if __name__ == "__main__":
    source_adapter = FTPDataSourceAdapter()
    transformation = ExcelDataTransformation()
    destination_adapter = DjangoDataSaverImpl()

    engine = FTPEngine()
    success = engine.synchronize(source_adapter, transformation, destination_adapter)

    if success:
        print("Data saved successfully to Django model.")
    else:
        print("Failed to save data to Django model.")




