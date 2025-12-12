import process_data


def main(data_file_path):

    data = process_data.main(data_file_path)
    

if __name__ == '__main__':

    data_file_path = './data.xlsx'
    main(data_file_path)