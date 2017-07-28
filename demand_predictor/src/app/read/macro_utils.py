# necessary imports
import os, sys
import win32com.client
import macro_generator as generator


class MacroHelper:
    def __init__(self, path):
        self.path = path
        self.path_to_excel_file = self.path[:-8] + '\\sample_data\\test_macro.xlsm'
        self.path_to_external_excel_file = None
        self.excel = None
        self.excel_external = None
        self.workbook = None
        self.workbook_external = None

    def open_workbook(self):
        self.terminate()
        try:
            self.excel = win32com.client.Dispatch("Excel.Application")
            self.excel.Visible = False
            self.workbook = self.excel.Workbooks.Open(Filename=self.path_to_excel_file)

            self.excel_external = win32com.client.Dispatch("Excel.Application")
            self.excel_external.Visible = False
            self.workbook_external = self.excel.Workbooks.Open(Filename=self.path_to_external_excel_file)
        except Exception as e:
            print "import error: ", e
            print "Please import again"
            self.terminate()

    def execute_macro(self, macro_type, field_name="empty", value=None):
        try:
            path_to_macro = self.path + '\\read\\' + macro_type + ".txt"
            macro_name = ""
            if macro_type == "get_filter":
                if field_name == "empty":
                    print "Field Name Cannot Be Empty!"
                output_path = self.path + '\\' + "read\\" + field_name + "_output.txt"
                macro_name = generator.generate_filter_macro(field_name, output_path, path_to_macro)
            elif macro_type == "change_pivot":
                if field_name == "empty":
                    print "Field Name Cannot Be Empty!"
                if value is None:
                    print "Value Cannot Be Empty!"
                if len(value) > 1:
                    macro_name = generator.generate_pivot_macro_multiple(field_name, value, path_to_macro)
                else:
                    macro_name = generator.generate_pivot_macro(field_name, value[0], path_to_macro)

            with open(path_to_macro, "r") as my_file:
                # print('reading macro into string from: ' + str(my_file))
                macro = my_file.read()

            excel_module = self.workbook.VBProject.VBComponents.Add(1)
            excel_module.CodeModule.AddFromString(macro)

            # print "test_macro.xlsm!" + macro_name[:-2]
            self.excel_external.Application.Run("test_macro.xlsm!" + macro_name[:-2])
            self.workbook_external.Save()
            self.workbook.Save()
            # excel.Application.Run(macro_name[:-2])
            return macro_name
        except Exception as e:
            return "NA"

    def clear_macro(self):
        try:
            for i in self.workbook.VBProject.VBComponents:
                xl_module = self.workbook.VBProject.VBComponents(i.Name)
                if xl_module.Type in [1, 2, 3]:
                    self.workbook.VBProject.VBComponents.Remove(xl_module)

        except Exception as e:
            pass

    def terminate(self):
        try:
            self.clear_macro()
            self.excel.Workbooks(1).Close(SaveChanges=1)
            self.excel.Application.Quit()
            self.excel_external.Application.Quit()

        except Exception as e:
            pass

