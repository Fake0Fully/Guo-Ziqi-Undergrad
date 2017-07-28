def generate_pivot_macro(field_name, value, macro_path):
    macro_file = open(macro_path, "r")
    version = int(macro_file.readline().split("_")[1]) + 1
    macro_file.close()
    content = "Sub macro_" + str(version) + "_pivot()\nDim pf As PivotField\n" \
                                            "Worksheets(\"Piv_Crawl_WT_CU_pcs\").Activate\n" \
                                            "Set division = ActiveSheet.PivotTables(\"PivotTable1\")" \
                                            ".PivotFields(\"" + field_name + "\")\n" \
                                                                             "division.ClearAllFilters\n" \
                                                                             "division.CurrentPage = \"" + value + \
              "\"\nEnd Sub\n "

    macro_file = open(macro_path, "w")
    macro_file.write(content)
    macro_file.close()
    return "macro_" + str(version) + "_pivot()"


def generate_pivot_macro_multiple(field_name, values, macro_path):
    macro_file = open(macro_path, "r")
    version = int(macro_file.readline().split("_")[1]) + 1
    macro_file.close()
    start_value = values[0]
    first_half = "Sub macro_" + str(version) + "_pivot()\n" \
                                               "Dim pf As PivotField\n" \
                                               "Worksheets(\"Piv_Crawl_WT_CU_pcs\").Activate\n" \
                                               "Set division = ActiveSheet.PivotTables(\"PivotTable1\")" \
                                               ".PivotFields(\"" + \
                 field_name + \
                 "\")\n" \
                 "division.ClearAllFilters\n" \
                 "division.EnableMultiplePageItems = True\n" \
                 "first_division = \"" + \
                 start_value + \
                 "\"\n" \
                 "For Each pvItem In division.PivotItems\n" \
                 "c = c + 1\n" \
                 "If pvItem.Name = first_division Then Exit For\n" \
                 "Next pvItem\n" \
                 "division.PivotItems(c).Visible = True\n" \
                 "For i = 1 To c - 1\n" \
                 "division.PivotItems(i).Visible = False\n" \
                 "Next\n" \
                 "For i = c + 1 To division.PivotItems.Count\n" \
                 "division.PivotItems(i).Visible = False\n" \
                 "Next\n"

    second_half = ""
    for i in range(1, len(values)):
        second_half += "division.PivotItems(\"" + values[i] + "\").Visible = True\n"
    second_half += "End Sub"
    content = first_half + second_half
    macro_file = open(macro_path, "w")
    macro_file.write(str(content))
    macro_file.close()
    return "macro_" + str(version) + "_pivot()"


def generate_filter_macro(field_name, output_path, macro_path):
    macro_file = open(macro_path, "r")
    version = int(macro_file.readline().split("_")[1]) + 1
    macro_file.close()
    new_field_name = field_name
    if isinstance(field_name, str):
        new_field_name = "\"" + field_name + "\""
    content = "Sub getfilter_" + str(version) + "_()\nApplication.ScreenUpdating = False\n" \
                                                "Sheets(\"Piv_Crawl_WT_CU_pcs\").Activate\nPiv_Sht = ActiveSheet.Name\n" \
                                                "Dim fso As Object\n" \
                                                "Set fso = CreateObject(\"Scripting.FileSystemObject\")\n" \
                                                "content = \"\"\n" \
                                                "For Each PivotItem In ActiveSheet.PivotTables(1)" \
                                                ".PageFields(" \
              + str(new_field_name) + ").PivotItems\n" \
                                      "content = content + PivotItem.Value + " \
                                      "\"@\"\n" \
                                      "Next\nDim Fileout As Object\n" \
                                      "Set Fileout = fso.CreateTextFile(\"" \
              + output_path + "\", True, True)\n" \
                              "Fileout.Write content\nFileout.Close\nSheets(Piv_Sht).Select\nEnd Sub "

    macro_file = open(macro_path, "w")
    macro_file.write(content)
    macro_file.close()
    return "getfilter_" + str(version) + "_()"


# if __name__ == "__main__":
#     macro_path = "C:\\Users\\Liu Su\\PycharmProjects\\CapstoneInfineonSmartData\\src\\app\\read\change_pivot.txt"
#     generate_pivot_macro_multiple("Division_short", ["ATV", "CCS", "IPC"], macro_path)
