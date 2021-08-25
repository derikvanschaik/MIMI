from tkinter import font
import PySimpleGUI as sg 
from fonts import fonts_list 
def main():
    canvas = sg.Graph((100, 100), (0,0), (100, 100), key='-CANVAS-')
    layout = [[canvas]]
    list_of_fonts = fonts_list
    valid_fonts = [] 
    idx = 0 
    window = sg.Window('fonts tester', layout)
    while(idx < len(list_of_fonts)):
        event , values = window.read(timeout=1) 
        if event == sg.WIN_CLOSED:
            break 
        # try: 
        window['-CANVAS-'].draw_text('testing this font', (50, 50),font=list_of_fonts[idx] )
        valid_fonts.append(fonts_list[idx])
        # except Exception as e:
        #     print(f"{list_of_fonts[idx]} throws {e}")
        idx+= 1 
    window.close()
    print(valid_fonts) 
if __name__=="__main__":
    main() 

    