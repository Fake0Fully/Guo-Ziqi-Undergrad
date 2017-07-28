import src.prediction.predictor as predictor
import src.report.report_generator as generator

import src.app.interface_testing as ui
import src.app.read.data_parser as parser

if __name__ == "__main__":
    filename = "../sample_data/example_new.xlsm"
    data = parser.read(filename)
    division_short = "ATV"
    agg_package_pl = "LQFP"
    prediction_target = "actual_quarter"

    example_data = data[division_short][agg_package_pl]
    print "Data Loaded"

    prediction = predictor.predict(example_data, prediction_target, "LR")
    print "Prediction Generated"
    print prediction

    report = generator.generate_report()
    print "Report Generated"

    ui.run()
