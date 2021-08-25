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
    # finally we want to set the focus onto the input element 
    user_input.set_focus()

def delete_text_box(textbox):
    textbox.delete_bounding_box()
@@ -40,22 +42,47 @@ def draw_text_box(textbox, user_text):
    textbox.write_lines()
    textbox.draw_bounding_box()

def delete_text_boxes(textboxes):
    for textbox in textboxes:
        delete_text_box(textbox)

# event handler for 'delete' event
def delete_selected_text_boxes(texts, texts_to_others):
    # delete the boxes from canvases 
    selected_textboxes = [textbox for textbox in texts if textbox.get_selected() ]
    drag_textboxes = [texts_to_others[textbox] for textbox in texts if textbox.get_selected()] 
    delete_text_boxes(selected_textboxes)
    delete_text_boxes(drag_textboxes)
    # delete the references from texts and texts_to_others trackers. 
    for textbox in selected_textboxes:
        texts.remove(textbox)
        del texts_to_others[textbox] 


def main():
    canvas = sg.Graph(
        (500, 500), (0,0), (500, 500), key='-CANVAS-',
        background_color='white', enable_events=True, 
        )
    canvas_drag = sg.Graph(
        (500, 500), (0,0), (500, 500), key='-CANVAS-DRAG-',
        background_color='white', enable_events=True,drag_submits=True,  
        )
    no_drag_tab = sg.Tab('Dragging Off', [[canvas]])
    drag_tab = sg.Tab('Dragging On', [[canvas_drag]])
    tabs = sg.TabGroup([[drag_tab, no_drag_tab]])
    user_input = sg.Input('', key="-INPUT-", enable_events=True)
    layout = [[user_input, sg.Button("hey")], [canvas]]
    layout = [[user_input, sg.Button("Delete")], [tabs]]
    window = sg.Window('carriage return tester', layout).finalize() 

    user_input.bind('<Return>', '-RETURN-CHARACTER-') # make an event for the return character
    location = None
    texts = [] # list of text box figures drawn onto the main canvas (the non-draggable canvas)
    texts_to_others = { } # for each textbox we have a corresponding text box figure drawn onto the other canvas.

    while True:
        event , values = window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            break
        if event == '-RETURN-CHARACTER-':
    def main():
                user_text = values['-INPUT-']
                text_at_click_location = get_text_box_at_location(location, texts)
                if text_at_click_location is None: # no text at current location, user is trying to create a new textbox here. 
                    text_at_click_location = Text(location, canvas) # create new text
                    # create new text onto both canvases 
                    text_at_click_location = Text(location, canvas)
                    text_on_drag_canvas = Text(location, canvas_drag)
                    # key value pairing for easy and efficient tracking when dragging event occurs.
                    texts_to_others[text_at_click_location] = text_on_drag_canvas
                    texts.append(text_at_click_location) # append it to list for tracking 
                else:
                    delete_text_box(text_at_click_location)
                    delete_text_box(text_at_click_location) 
                    delete_text_box(text_on_drag_canvas) 
                    # this is required for a subtle reason -- when rewriting into text boxes 
                    # and the textbox happens to be a multiple line textbox: if you backspace to a previous line 
                    # the older location of a click may sometimes no longer be valid and cause a bug where 
                    # rewriting the same text into a new textbox somewhere near. This is the solution to this bug: 
                    location = text_at_click_location.location

                draw_text_box(text_at_click_location, user_text)
                draw_text_box(text_on_drag_canvas, user_text)  

            except Exception as e:
                sg.popup(f"This action returned the following error: \n\t'{e}'.\nYou probably forgot to click where you want to type!") 

                sg.popup(f"This action returned the following error: \n\t'{e}'.\nYou probably forgot to click where you want to type!")

        if event == "Delete":
            delete_selected_text_boxes(texts, texts_to_others)

    window.close()

if __name__=="__main__":
    main() 