import xlsxwriter
import datetime
class save_to_xlsx:
    sheet_index = 0;
    def __init__(self, file_name='noname'):
        if(file_name == 'noname'):
            today = datetime.datetime.today()
            self.xlsx_name = str(today.strftime('test_%Y%m%d_%H%M%S.xlsx'))
        else:
            self.xlsx_name = file_name
        self.workbook = xlsxwriter.Workbook(self.xlsx_name)
        self.config_format()
        self.headform = self.workbook.add_format(self.header_format)
        self.dataform = self.workbook.add_format(self.data_format)
    def config_format(self):
        self.header_format = {
            'bold' : 1,
            'border' : 1,
            'align' : 'center',
            'pattern' : 1,
            'bg_color' : '#D9D9D9'}
        self.data_format = {
            'border' : 1,
            'align' : 'center'}
        self.column_width = 20
    def add_sheet(self, sheet_name='noname'):
        if(sheet_name == 'noname'):
            now = datetime.datetime.today()
            self.sheet_name = str(now.strftime('%Y%m%d_%H%M%S_')) + str(save_to_xlsx.sheet_index)
            save_to_xlsx.sheet_index += 1
        else:
            self.sheet_name = sheet_name;
        self.worksheet = self.workbook.add_worksheet(self.sheet_name)
        self.row = 0
        self.col = 0
    def write_head(self, head=['Tab1', 'Tab2', 'Tab3', 'Tab4', 'Tab5', 'Tab6', 'Tab7', 'Tab8']):
        for item in head:
            self.worksheet.write(self.row, self.col, item, self.headform)
            self.col += 1
        self.row += 1
        self.col = 0
    def write_data(self, data_list):
        for data in data_list:
            self.worksheet.write(self.row, self.col, data, self.dataform)
            self.col += 1
        self.row += 1
        self.col = 0
    def close(self):
        self.workbook.close()

if __name__ == '__main__':
    Head = ['item1', 'item2', 'item3', 'item4', 'item5', 'item6', 'item7', 'item8']
    Data = [10, 20, 30, 40, 50, 60, 70, 80]
    save_xlsx = save_to_xlsx('test_01.xlsx')
    save_xlsx.add_sheet('sim_01')
    save_xlsx.write_head(Head)
    save_xlsx.write_data(Data)
    save_xlsx.write_data(Data)
    save_xlsx.write_data(Data)
    save_xlsx.close()
    save_xlsx2 = save_to_xlsx()
    save_xlsx2.add_sheet()
    save_xlsx2.write_data(Data)
    save_xlsx2.write_data(Data)
    save_xlsx2.write_data(Data)
    save_xlsx2.write_data(Data)
    save_xlsx2.add_sheet('second')
    save_xlsx2.write_head(Head)
    save_xlsx2.write_data(Data)
    save_xlsx2.write_data(Data)
    save_xlsx2.write_data(Data)
    save_xlsx2.close()

