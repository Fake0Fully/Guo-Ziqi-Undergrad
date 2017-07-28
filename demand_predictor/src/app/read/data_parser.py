import pandas as pd
import macro_utils

def read_excel(filename, reference):
    xls = pd.ExcelFile(filename)
    ref_df = pd.read_csv(reference, thousands=",")
    ref_df.drop(ref_df.columns[[-1]], axis=1, inplace=True)

    df = xls.parse('Piv_Crawl_WT_CU_pcs', skiprows=16, index_col=None, na_values=['NA']).iloc[:-1]
    df.drop(df.columns[[0]], axis=1, inplace=True)
    new_df = pd.concat([ref_df, df], axis=1)
    # print new_df

    last_column = list(ref_df)[-1].split("Q")

    current_year = int(last_column[0])
    current_quarter = int(last_column[1])
    current_columns = list(new_df)
    for i in range(4):
        if current_quarter + 1 > 4:
            current_quarter = 1 + current_quarter - 4
            current_year += 1
        else:
            current_quarter += 1
        current_columns[-4 + i] = str(current_year) + "Q" + str(current_quarter)

    new_df.columns = current_columns

    # new_df.to_csv(reference, index=False)

    return new_df


def read(macro_helper, filename, reference_path, division=None):
    # macro_helper.execute_macro("get_filter", "Division_short")
    # macro_helper.execute_macro("change_pivot", "Division_short", division)

    return read_excel(filename, reference_path)


if __name__ == "__main__":
    # path = "C:\Users\Liu Su\PycharmProjects\CapstoneInfineonSmartData\sample_data\\data.xlsm"
    # ref_path = "C:\Users\Liu Su\PycharmProjects\CapstoneInfineonSmartData\sample_data\\test_consolidated_data_atv.csv"
    # read(path, ref_path, division=["PMM"])
    read_excel("C:\Users\Liu Su\PycharmProjects\CapstoneInfineonSmartData\sample_data\\data.xlsm",
               "C:\Users\Liu Su\PycharmProjects\CapstoneInfineonSmartData\sample_data\\consolidated_data_atv.csv" )
