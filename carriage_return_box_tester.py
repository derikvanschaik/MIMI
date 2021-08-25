from os import write
from tkinter.constants import S
import PySimpleGUI as sg
from text import Text
import json
import os 
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
            user_input.update(text_at_click_location.get_lines()) 
        else:
            text_at_click_location.delete_selected_box() 
    else:
        user_input.update("") # we want to clear user input so user can start typing
    # finally we want to set the focus onto the input element 
    user_input.set_focus()

def delete_text_box(textbox):
    textbox.delete_bounding_box()
    textbox.delete_lines()

def draw_text_box(textbox, user_text):
    # sometimes we may not want to use this function to draw new text
    # when we already have text and just want to draw 
    # same text at say a given new location when dragging
    # for which we would simply set None as user_text param.   
    if user_text:
        textbox.put_lines(user_text) 
    textbox.write_lines()
    textbox.draw_bounding_box()

def delete_text_boxes(textboxes):
    for textbox in textboxes:
        delete_text_box(textbox)

def move_text_box(textbox, new_location):
    delete_text_box(textbox)
    textbox.change_location(new_location)   
    draw_text_box(textbox, None) # draw textbox at new location 

def get_selected_text_boxes(textboxes):
    return [textbox for textbox in textboxes if textbox.get_selected() ] 

def switch_tabs(drag_button, drag_tab, no_drag_tab):
    drag_button_text = drag_button.get_text() 
    if drag_button_text == "Drag mode: OFF":
        drag_tab.update(visible=True)
        drag_tab.select() 
        no_drag_tab.update(visible=False)
        drag_button.update(text = f"Drag mode: ON")
    else:
        drag_tab.update(visible=False)
        no_drag_tab.select() 
        no_drag_tab.update(visible=True) 
        drag_button.update(text = f"Drag mode: OFF")

def enable_and_disable_buttons_and_inputs(drag_button_text, user_input, selected_texts, delete_button, connect_button):
    user_input.update( disabled = (drag_button_text == "Drag mode: ON") ) # want to disable user input if in drag mode
    delete_button.update( disabled = not(len(selected_texts) > 0) )
    connect_button.update( disabled = not(len(selected_texts) == 2 ) )

def save_canvas(texts, lines_to_locs):
    saved_canvas = {
        'textboxes': [], 
        'lines': [], 
    }
    for textbox in texts:
        tbox_rep = {}
        tbox_rep['location'] = list( textbox.get_location() ) # convert all tuples to list for json saving. 
        tbox_rep['lines'] = textbox.lines # list data structure
        tbox_rep['font_name'] = textbox.font_name 
        tbox_rep['font_size'] = textbox.font_size
        tbox_rep['background_color'] = textbox.background_color
        tbox_rep['line_color'] = textbox.line_color
        tbox_rep['text_color'] = textbox.text_color 
        saved_canvas['textboxes'].append( tbox_rep)
    
    for (from_loc, to_loc) in lines_to_locs.values():
        saved_canvas['lines'].append( [list(from_loc), list(to_loc) ]) # convert all tups to list for json

    return saved_canvas 

# helper method used in load canvas to copy textbox object dictionary reference 
# into a textbox object. Purpose is to instantiate textbox object and copy fields over. 
def dict_to_textbox(textbox_rep, canvas):
    location = tuple(textbox_rep['location']) 
    textbox = Text(location, canvas)
    textbox.lines = textbox_rep['lines']
    textbox.font_name = textbox_rep['font_name']
    textbox.font_size = textbox_rep['font_size']
    textbox.background_color = textbox_rep['background_color']
    textbox.line_color = textbox_rep['line_color']
    textbox.text_color = textbox_rep['text_color']
    return textbox  


def load_canvas(saved_canvas, texts, texts_to_others,  lines_to_locs, lines_to_others, canvas, canvas_drag):
    for textbox_rep in saved_canvas['textboxes']:
        textbox = dict_to_textbox(textbox_rep, canvas)
        textbox_drag = dict_to_textbox(textbox_rep, canvas_drag) 
        draw_text_box(textbox, None) # None as we already have text in lines property. 
        draw_text_box(textbox_drag, None) 
        texts.append(textbox)
        texts_to_others[textbox] = textbox_drag 
    
    for [from_loc, to_loc] in saved_canvas['lines']:
        # convert from list back to tuples (undo what we did in save canvas function)
        from_loc = tuple(from_loc) 
        to_loc = tuple(to_loc)
        line_main = canvas.draw_line(from_loc, to_loc)
        line_drag = canvas_drag.draw_line(from_loc, to_loc)
        canvas.send_figure_to_back(line_main)
        canvas_drag.send_figure_to_back(line_drag) 
        lines_to_others[line_main] = line_drag 
        lines_to_locs[line_main] = (from_loc, to_loc)

def open_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def write_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def get_json_file_list():
    json_file_list = [] 
    for entry in os.scandir('.'):
        if entry.is_file():
            if entry.name.endswith('.json'):
                json_file_list.append(entry.name)
    return json_file_list 

def select_files_window(file_list):
    layout = [[sg.Listbox(file_list, key='-FILE-CHOICE-', size=(10, len(file_list)))], [sg.B('Open File')] ]  
    win = sg.Window('Select File', layout)
    selected_file = None 
    while True:
        event, values = win.read()
        # print(event, values) 
        if event in (sg.WIN_CLOSED, None):
            break
        if event == 'Open File':
            # print("selecting", values['-FILE-CHOICE-'] ) 
            selected_file = values['-FILE-CHOICE-'][0] 
            break 
    win.close() 
    return selected_file 

def save_file_as_window():
    layout = [[sg.Input('', key='filename')], [sg.Button('Save')] ]  
    win = sg.Window('Save file under desired name.', layout) 
    filename = None 
    while True:
        event, values = win.read()
        # print(event, values) 
        if event in (sg.WIN_CLOSED, None):
            break
        if event == 'Save':
            if values['filename']:
                filename = values['filename']
                break
        
    win.close() 
    return filename 


def main():
    #build theme 
    sg.theme(sg.theme_list()[19]) # randomly chose this and like
    sg.theme_background_color('lightblue')
    sg.theme_element_background_color('lightyellow')
    sg.theme_button_color(('black', 'white'))
    #layout widgets 
    canvas = sg.Graph(
        (800, 600), (0,0), (500, 500), key='-CANVAS-',
        background_color='white', enable_events=True, 
        )
    canvas_drag = sg.Graph(
        (800, 600), (0,0), (500, 500), key='-CANVAS-DRAG-',
        background_color='white', enable_events=True,drag_submits=True,
        )
    no_drag_tab = sg.Tab('Dragging Off', [[canvas]])
    drag_tab = sg.Tab('Dragging On', [[canvas_drag]], visible = False ) 
    tabs = sg.TabGroup([[no_drag_tab, drag_tab]])
    save_json_button = sg.Button("save current canvas") 
    connect_button = sg.Button("connect selected boxes")
    delete_button = sg.Button("Delete") 
    drag_mode_button = sg.Button("Drag mode: OFF", key="-TOGGLE-DRAG-MODE-")
    clear_canvas_button = sg.Button("clear canvas")
    load_json_button = sg.Button("load saved")
    user_input = sg.Input('', key="-INPUT-", enable_events=True, 
                            background_color=sg.theme_background_color(),
                            text_color=sg.theme_background_color(), 
                          )
    menu_def = [['File', ['Open', 'Save', 'Save As']]]  
    menu = sg.Menu(menu_def) 
    layout = [
        [menu],  
        [drag_mode_button, connect_button, delete_button, save_json_button, load_json_button, clear_canvas_button], 
        [tabs],
        [user_input]
            ]
    window = sg.Window('carriage return tester', layout).finalize()
    # final bindings and widget modifications prior to event loop 
    user_input.bind('<Return>', '-RETURN-CHARACTER-') # make an event for the return character
    user_input.set_cursor(cursor_color=sg.theme_background_color() ) # now this element is virtually 'invisible' 
    canvas.set_focus() # we want focus away from input to stop a bug
    connect_button.update(disabled=True) 
    delete_button.update(disabled=True)
    # global event variables 
    location = None 
    texts = [] # list of text box figures drawn onto the main canvas (the non-draggable canvas)
    texts_to_others = {} # for each textbox we have a corresponding text box figure drawn onto the other canvas -this maps the two.
    lines_to_others = {} # same as above except with lines 
    lines_to_locs = {} # map each line figure to a tuple of from_location, to_location points. 
    saved_canvas = {} # data structure we will use to save the contents of the current canvas 
    filename = None 
    while True: 
        event , values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '-RETURN-CHARACTER-':
            # append return character to current text 
            window['-INPUT-'].update( 
                values['-INPUT-'] + RETURN_CHAR # text box splits based on return char 
            )
        if event == "-CANVAS-":
            location = values[event] # location of click
            handle_canvas_click(location, texts, user_input)
        
        if event.startswith("-CANVAS-DRAG-"):
            x_click, y_click = values['-CANVAS-DRAG-']
            threshold = 15 
            for textbox in texts:
                x, y = textbox.get_location()
                if abs(x-x_click) <= threshold and abs(y-y_click) <= threshold:
                    # move the textbox as it is being dragged 
                    new_location = (x_click, y_click)
                    move_text_box(textbox, new_location) 
                    move_text_box(texts_to_others[textbox], new_location) # this is the actual textbox we are moving on drag canvas  
                    # find all lines associated with this location 
                    for figure in canvas.get_figures_at_location((x, y)):
                        if figure in lines_to_others: # figure is a line 
                            canvas.delete_figure(figure) # delete from canvas
                            canvas_drag.delete_figure(lines_to_others[figure] ) # delete line from drag canvas 
                            del lines_to_others[figure] # remove reference
                            (from_loc, to_loc) = lines_to_locs[figure]
                            new_from_loc = None 
                            new_to_loc = None 
                            if (x, y) == (from_loc):
                                new_from_loc = (x_click, y_click)
                                new_to_loc = to_loc
                            else:
                                new_from_loc = from_loc
                                new_to_loc = (x_click, y_click)
                            line_main = canvas.draw_line(new_from_loc, new_to_loc)
                            line_drag = canvas_drag.draw_line(new_from_loc, new_to_loc)
                            canvas.send_figure_to_back(line_main)
                            canvas_drag.send_figure_to_back(line_drag)
                            lines_to_others[line_main] = line_drag
                            lines_to_locs[line_main] = (new_from_loc, new_to_loc)
                            del lines_to_locs[figure] # delete old reference as ids are constantly changed 

                

        if event.startswith("-INPUT-"):
            # we only want to execute this code when NOT in drag mode 
            if drag_mode_button.get_text() == "Drag mode: OFF": 

                if event == "-INPUT--RETURN-CHARACTER-":
                    window['-INPUT-'].update( 
                            values['-INPUT-'] + RETURN_CHAR # text box splits based on return char 
                                )

                user_text = values['-INPUT-']
                text_at_click_location = get_text_box_at_location(location, texts)
                try:
                    if text_at_click_location is None: # no text at current location, user is trying to create a new textbox here. 
                        # create new text onto both canvases 
                        text_at_click_location = Text(location, canvas)
                        text_on_drag_canvas = Text(location, canvas_drag)
                        # key value pairing for easy and efficient tracking when dragging event occurs.
                        texts_to_others[text_at_click_location] = text_on_drag_canvas
                        texts.append(text_at_click_location) # append it to list for tracking 
                    else:
                        
                        delete_text_box(text_at_click_location) 
                        delete_text_box(texts_to_others[text_at_click_location])  
                        # this is required for a subtle reason -- when rewriting into text boxes 
                        # and the textbox happens to be a multiple line textbox: if you backspace to a previous line 
                        # the older location of a click may sometimes no longer be valid and cause a bug where 
                        # rewriting the same text into a new textbox somewhere near. This is the solution to this bug: 
                        location = text_at_click_location.get_location()

                    text_at_click_location.put_lines(user_text) 
                    draw_text_box(text_at_click_location, user_text)
                    draw_text_box(texts_to_others[text_at_click_location], user_text)  

                except Exception as e:
                    print(e) # logging error to output for now

            else: # user has likely forgotten to turn off drag mode. 
                sg.popup("Turn off Drag Mode to start typing on canvas again :). ")
        
        if event == "Delete":
            selected_textboxes = get_selected_text_boxes(texts)
            locations = [textbox.get_location() for textbox in selected_textboxes]
            for location in locations:
                for figure in canvas.get_figures_at_location(location):
                    if figure in lines_to_others:
                        canvas.delete_figure(figure)
                        canvas_drag.delete_figure(lines_to_others[figure]) 
                        del lines_to_others[figure] # delete the reference 
                        del lines_to_locs[figure] # delete reference to locations 

            for textbox in selected_textboxes:
                delete_text_box(textbox)
                delete_text_box(texts_to_others[textbox])
                texts.remove(textbox)
                del texts_to_others[textbox] 
                
        if event == "connect selected boxes":
            selected_textboxes = get_selected_text_boxes(texts)
            [from_loc, to_loc] = [textbox.get_location() for textbox in selected_textboxes]
            # updates the references for these lines drawn at location for later -- will need for deleting and dragging 
            line_on_main = canvas.draw_line(from_loc, to_loc)
            line_on_drag = canvas_drag.draw_line(from_loc, to_loc)
            canvas.send_figure_to_back(line_on_main)
            canvas_drag.send_figure_to_back(line_on_drag) 

            lines_to_others[line_on_main] = line_on_drag # reference for later
            lines_to_locs[line_on_main] = (from_loc, to_loc)  
            for textbox in selected_textboxes:
                textbox.delete_selected_box()
                textbox.toggle_selected() 
                      
        if event == "-TOGGLE-DRAG-MODE-":
            switch_tabs(drag_mode_button, drag_tab, no_drag_tab)
        
        # EVENTS RELATED TO PERSISTENCE -- IN TESTING (BETA) MODE. 
        if event == "save current canvas":
            # save canvas into data structure for json 
            saved_canvas = save_canvas(texts, lines_to_locs)
            # convert saved_canvas into json and write to file for persistence 

        
        if event == "clear canvas":
            if saved_canvas:
                # erase all figures from canvas
                canvas_drag.erase()
                canvas.erase()
                # re init all tracking data structures -- remove all references 
                texts = [] 
                lines_to_locs = {}
                lines_to_others = {} 


        if event == "load saved":

            load_canvas(
                saved_canvas, texts, texts_to_others, 
                lines_to_locs, lines_to_others,
                canvas, canvas_drag
                )
        
        if event in ('Open', "Save", "Save As"):
            if event == 'Save':
                if filename:
                    saved_canvas = save_canvas(texts, lines_to_locs)
                    write_file(filename, saved_canvas)
                else:
                    sg.popup('There is no currently associated filename with your canvas.\n Please try "Saving as" your desired filename.')
            if event == 'Save As':
                # save canvas into data structure for json 
                saved_canvas = save_canvas(texts, lines_to_locs)
                filename = save_file_as_window() + '.json' # user simply provides name 
                if filename:
                    write_file(filename, saved_canvas) # write saved canvas to json 
            
            if event == 'Open':
                json_files = get_json_file_list()
                filename = select_files_window(json_files)
                print(filename)
                if filename:
                    saved_canvas = open_file(filename)# reference to us opening files 
                    # erase all figures from canvas
                    canvas_drag.erase()
                    canvas.erase()
                    # re init all tracking data structures -- remove all references 
                    texts = [] 
                    lines_to_locs = {}
                    lines_to_others = {}
                    load_canvas(
                        saved_canvas, texts, texts_to_others, 
                        lines_to_locs, lines_to_others,
                        canvas, canvas_drag
                    )
                



        # want to disable and enable buttons based on certain conditions
        # so that the user can't fire certain events based on these conditions 
        enable_and_disable_buttons_and_inputs( 
            drag_mode_button.get_text(), 
            user_input, get_selected_text_boxes(texts), 
            delete_button, connect_button
        )

           


    window.close()

if __name__=="__main__":
    main() 
