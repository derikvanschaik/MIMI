import PySimpleGUI as sg
from text import Text
# GLOBAL CONSTANTS 
RETURN_CHAR = "\\"

# Returns Text object if there is a text box at given location, none otherwise. 
def get_text_box_at_location(click_location, text_boxes):
    x_click, y_click = click_location
    for text in text_boxes:
        top_left, bott_right= text.get_bounding_coordinates()
        x_left, top_y = top_left 
        x_right, bott_y = bott_right
        # the user clicked on an already present textbox 
        if x_click in range(x_left, x_right +1) and y_click in range(bott_y, top_y+1):
            return text 
    return None # no textbox at given location 

def handle_canvas_click(click_location, text_boxes, user_input):
    text_at_click_location = get_text_box_at_location(click_location, text_boxes)
    # fill user input with text present in textbox so they can append new text. 
    if text_at_click_location:
        text_at_click_location.toggle_selected()
        is_selected = text_at_click_location.get_selected() # get the selected property 
        if is_selected:
            text_at_click_location.draw_selected_box()

        else:
            text_at_click_location.delete_selected_box() 

        user_input.update(text_at_click_location.get_lines()) 
    else:
        user_input.update("") # we want to clear user input so user can start typing

def delete_text_box(textbox):
    textbox.delete_bounding_box()
    textbox.delete_lines()

def draw_text_box(textbox, user_text):
    textbox.put_lines(user_text) 
    textbox.write_lines()
    textbox.draw_bounding_box()


def main():
    canvas = sg.Graph(
        (500, 500), (0,0), (500, 500), key='-CANVAS-',
        background_color='white', enable_events=True, 
        )
    user_input = sg.Input('', key="-INPUT-", enable_events=True)
    layout = [[user_input, sg.Button("hey")], [canvas]]
    window = sg.Window('carriage return tester', layout).finalize() 
    user_input.bind('<Return>', '-RETURN-CHARACTER-') # make an event for the return character
    location = None
    texts = [] # list of text box figures drawn onto the main canvas (the non-draggable canvas)
    texts_to_others = { } # for each textbox we have a corresponding text box figure drawn onto the other canvas.

    while True:
        event , values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '-RETURN-CHARACTER-':
            print("hey there I am here")
            window['-INPUT-'].update( 
                values['-INPUT-'] + RETURN_CHAR # text box splits based on return char 
            )
        if event == "-CANVAS-":
            location = values[event] # location of click 
            handle_canvas_click(location, texts, user_input)

        if event.startswith("-INPUT-"):

            if event == "-INPUT--RETURN-CHARACTER-":
                window['-INPUT-'].update( 
                        values['-INPUT-'] + RETURN_CHAR # text box splits based on return char 
                            )
            try:
                user_text = values['-INPUT-']
                text_at_click_location = get_text_box_at_location(location, texts)
                if text_at_click_location is None: # no text at current location, user is trying to create a new textbox here. 
                    text_at_click_location = Text(location, canvas) # create new text
                    texts.append(text_at_click_location) # append it to list for tracking 
                else:
                    delete_text_box(text_at_click_location)
                    # this is required for a subtle reason -- when rewriting into text boxes 
                    # and the textbox happens to be a multiple line textbox: if you backspace to a previous line 
                    # the older location of a click may sometimes no longer be valid and cause a bug where 
                    # rewriting the same text into a new textbox somewhere near. This is the solution to this bug: 
                    location = text_at_click_location.location

                draw_text_box(text_at_click_location, user_text)

            except Exception as e:
                sg.popup(f"This action returned the following error: \n\t'{e}'.\nYou probably forgot to click where you want to type!") 


    window.close()

if __name__=="__main__":
    main() 
