from docx2pdf import convert

input_path = r"f:\2CentCapital\aryan-price-action-framework\docs\ARYAN_PRICE_ACTION_INDICATOR_PAPER.docx"
output_path = r"f:\2CentCapital\aryan-price-action-framework\docs\ARYAN_PRICE_ACTION_INDICATOR_PAPER.pdf"

convert(input_path, output_path)
print('Converted:', output_path)
