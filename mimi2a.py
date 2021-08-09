import PySimpleGUI as sg
import fonts 

# param types: tuple, dict, PysimpleGUI graph widget 
# Deletes textbox figures and the text bounding box 
def delete_previous_drawn_figures(click_location, figures, canvas):
    for figure in canvas.get_figures_at_location(click_location):
        canvas.delete_figure(figure)
        if figure in figures:
            figure_type = figures[figure]['type']
            if figure_type == "text":
                canvas.delete_figure(figures[figure]['bounding-box']) # we need to delete the bounding box as well for text figures 

            del figures[figure] # remove the reference of this figure in the figures dictionary 

def get_selected_text_figures(figures):
    selected_figures = [] 
    for figure in figures.keys():
        figure_type = figures[figure]['type']
        if figure_type == "text":
            if figures[figure]['selected']:
                selected_figures.append(figure)
    return selected_figures 

# returns a tupe of tuples of figure ids and figure locations 
def get_location_of_figures(list_of_figures, figures_on_drag_canvas):
    locations = [] 
    for figure in figures_on_drag_canvas.keys():
        figure_id = figures_on_drag_canvas[figure]["main-canvas-reference"]
        if figure_id in list_of_figures:
            location = figures_on_drag_canvas[figure]["main-canvas-location"] # location of figure
            locations.append( (figure_id, location) )
    return tuple(locations)

# helper function used in '-CONNECT-' event 
def get_figures_on_drag_ids(list_of_figures, figures_on_drag_canvas): # canvas param being used for debugging
    ids = []
    # print(list_of_figures)
    for figure in figures_on_drag_canvas.keys():
        ref_id = figures_on_drag_canvas[figure]["main-canvas-reference"] 
        if ref_id in list_of_figures:
            ids.append(figure) 
    return ids

def get_lines_at_location(location, figures):
    lines = [] 
    for figure in figures.keys():
        if figures[figure]["type"] == "line": 
            loc1, loc2 = figures[figure]["locations"]
            if loc1 == location or loc2 == location:
                lines.append(figure)
    return lines 

# Deletes the selected bounding box of the screen - note it does not 
# turn the 'selected' property to False in the dictionary 
def remove_selected_bounding_box(figures, figure, canvas):
    selected_bounding_box = figures[figure]['selected-bounding-box']
    canvas.delete_figure( selected_bounding_box)
    # remove the reference  
    figures[figure]['selected-bounding-box'] = None

# helper function for draw_text_and_box_figures: 
def update_main_canvas_dict(figures, new_text_id, bounding_box_id, text):
    # add newly drawn text id to figures dict
    figures[new_text_id] = {
                            "type": "text",
                            "text": text,
                            "selected": False,
                            "bounding-box":bounding_box_id, 
                            "selected-bounding-box":None, # draw this when user selects this figure 
                                }
# helper function for draw_text_and_box_figures: 
def update_drag_canvas_dict(figures_on_drag_canvas, text, new_text_id_drag, bounding_box_id_drag, new_text_id, click_location):
    figures_on_drag_canvas[new_text_id_drag] = {
                                "type": "text",
                                "text": text, 
                                "bounding-box": bounding_box_id_drag,
                                # **IMPORTANT** we need to keep the reference to 
                                # the id of the text id on main canvas when we 'drag' and move this 
                                # text and bounding box on the drag canvas so that when user gets out of drag
                                # mode the text and bounding box are in their new positions. 
                                "main-canvas-reference": new_text_id,
                                # We need to keep track of the main canvas location too for when we 
                                # move and drag elements in drag mode 
                                "main-canvas-location": click_location, 
                                            }

# Returns -> None 
def draw_text_and_box_figures(text,click_location, font_size, canvas, figures, canvas_with_drag, figures_on_drag_canvas ):
    # create new figures to draw at location on main canvas, the figures which are the user text and the corresponding bounding box. 
    # text = values[event]
    print("IN draw and text box figures! ") 
    new_text_id  = canvas.draw_text(text, click_location, font = f"default {font_size}",  text_location=sg.TEXT_LOCATION_LEFT)
    top_left, bott_right  = canvas.get_bounding_box(new_text_id)
    bounding_box_id = canvas.draw_rectangle(top_left, bott_right, fill_color = "white", line_color="red")
    canvas.send_figure_to_back(bounding_box_id)
    # add newly drawn text id to figures dict
    update_main_canvas_dict(figures, new_text_id, bounding_box_id, text)
    # create new figures to draw at location on drag canvas. We need these to be drawn so that when user goes 
    # into drag mode, these widgets will be present on the drag canvas when they move them. 
    new_text_id_drag = canvas_with_drag.draw_text(text, click_location,  font = f"default {font_size}", text_location=sg.TEXT_LOCATION_LEFT)
        # same location as on main canvas so need to re init top_left and bott_right variables 
    bounding_box_id_drag = canvas_with_drag.draw_rectangle(top_left, bott_right, fill_color = "white", line_color="red")
    canvas_with_drag.send_figure_to_back(bounding_box_id_drag) 
    # add newly drawn text id to figures on drag canvas dict 
    update_drag_canvas_dict(figures_on_drag_canvas, text, new_text_id_drag, bounding_box_id_drag, new_text_id, click_location)
    # need for reference for functions which need to update selected property of figures 
    return new_text_id, new_text_id_drag

def draw_bounding_box(canvas, figure, figures):
    top_left, bott_right  = canvas.get_bounding_box(figure)
    top_left_x, top_left_y = top_left
    bott_right_x, bott_right_y = bott_right
    pad = 5 
    top_left_x -= pad 
    top_left_y += pad
    bott_right_x += pad
    bott_right_y -= pad 
    top_left = (top_left_x, top_left_y)
    bott_right = (bott_right_x, bott_right_y)
    # update the bounding box in figures dict 
    figures[figure]['selected-bounding-box'] = canvas.draw_rectangle(top_left, bott_right, line_color="green")

def update_lines(fig_location, location, figures, canvas, canvas_with_drag):
    lines = get_lines_at_location(fig_location, figures) 
    for line in lines:
        moving_location_idx = figures[line]["locations"].index(fig_location)
        # change the moving loc reference in dict of line
        if moving_location_idx == 0:
            figures[line]["locations"] = ( 
                location, 
                figures[line]["locations"][1]
            )
        else:
            figures[line]["locations"] = (  
                figures[line]["locations"][0],
                location,
            )
        # variables referencing where new location and previous location where we will draw a new line at 
        point1, point2 = figures[line]["locations"]
        previous_lines = figures[line]["line-ids"] 
        line_on_main, line_on_drag = previous_lines
        # delete and redraw lines and assign their new id to line ids property 
        canvas.delete_figure(line_on_main)
        canvas_with_drag.delete_figure(line_on_drag)
        figures[line]["line-ids"] = (
            canvas.draw_line(point1, point2), 
            canvas_with_drag.draw_line(point1, point2) 
        )
        # send lines to back 
        line_on_main, line_on_drag = figures[line]["line-ids"]
        canvas.send_figure_to_back(line_on_main)
        canvas_with_drag.send_figure_to_back(line_on_drag )


def main():
    sg.theme("Material2") 
    bg_color = sg.theme_background_color() 
    # canvas is our main canvas which we do most of the drawing onto 
    canvas = sg.Graph((700,600), (0,0), (500, 500), enable_events=True, key='-CANVAS-', background_color="white")
    # we need a new canvas object to enable dragging 
    canvas_with_drag = sg.Graph((700,600), (0,0), (500, 500), enable_events=True, key='-CANVAS-DRAG-', drag_submits = True, background_color="white")
    # put each canvas element into their own seperate tabs -- we will only have one visible at a time in order to 
    # maintain the illusion that all this is occuring on the same canvas to the user 
    no_drag_tab = sg.Tab('Dragging Off', [[canvas]] )
    drag_tab = sg.Tab('Dragging On', [[canvas_with_drag]], visible=False) 
    tabs = sg.TabGroup([[no_drag_tab, drag_tab]]) 
    user_input = sg.Input('', key="-INPUT-", enable_events=True, text_color= bg_color, background_color=bg_color) 
    drag_button = sg.Button('Drag Mode Off', key = "-DRAG-", button_color = ("black", "green"))
    connect_button = sg.Button("Connect Boxes", key = "-CONNECT-",  button_color= ("black", "grey"), disabled = True) 
    delete_button = sg.Button("Delete selected figures", key = "-DELETE-", button_color = ("black", "grey"), disabled = True)
    font_size_slider = sg.Slider(range=(5 , 30), default_value=16,  enable_events=True, key="-FONT-SIZE-", orientation="horizontal")
    # fonts = get_font_list() 
    fonts_menu = sg.Combo(['default', 'no fun', 'yeehaw'], default_value='default', readonly=True)
    # Build the final layout 
    layout = [[ drag_button, connect_button, delete_button, sg.T("Font Size: "), font_size_slider, fonts_menu], [tabs] , [user_input]]
    window = sg.Window('mimi 2', layout).finalize()
    user_input.set_cursor(cursor_color=bg_color) # this is what makes this element invisible. 
    # global variables 
    cur_tab = 'Dragging Off' # tracks the current tab the user is on -- changes when user goes in and out of drag mode 
    click_location = (50, 50) # tracks the last clicked location - chose an arbitrary location as a defuault loc to begin writing if user doesn't click before writing. 
    figures = {} # dictionary of figures drawn onto the canvas where key is their id (integer)
    figures_on_drag_canvas = {} # dictionary keeping track of figures drawn onto canvas where dragging is enabled ! 
    drag_hotspot = None # global variable so we can have a drag hotspot to help user see where the dragging hotspot is -- ie where they should distance their
    # text box from others within this radius!
    line_count = 0 # experimenting this with line drawing
    font_size = 16

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break
        if event == "-FONT-SIZE-":
            font_size = int(values[event])
            selected_text_figs = get_selected_text_figures(figures)
            print(selected_text_figs)
            # print(font_size)
            for figure in selected_text_figs:
                [drag_figure] = get_figures_on_drag_ids([figure], figures_on_drag_canvas) # get corresponding figure on drag canvas
                location = figures_on_drag_canvas[drag_figure]["main-canvas-location"] # location of figure
                text = figures[figure]["text"] 
                # need to delete the bounding box of figure on canvas 
                remove_selected_bounding_box(figures, figure, canvas ) 
                delete_previous_drawn_figures(location, figures, canvas) # delete text figure on main canvas
                delete_previous_drawn_figures(location, figures_on_drag_canvas, canvas_with_drag) # delete corresponding figure on drag canvas
                # this function will drag both figures on both canvases and update both their dictionaries 
                new_text_id, new_text_id_drag = draw_text_and_box_figures(
                    text, location, font_size, canvas, figures,
                    canvas_with_drag, figures_on_drag_canvas
                )
                # need to update figures selected property
                figures[new_text_id]["selected"] = True 
                figures_on_drag_canvas[new_text_id_drag]['selected'] = True 
                # Need to redraw the bounding box for selected figures in selected_text_figs 
                draw_bounding_box(canvas, new_text_id, figures)
                # also need to update the lines that are at that location on the canvas 
                # note there is no difference between fig location and location argument so we just keep them the same 
                update_lines(location, location, figures, canvas, canvas_with_drag)


        if event == "-DRAG-":
            cur_tab = "Dragging Off" if cur_tab == "Dragging On" else "Dragging On" # toggle the current tab
            drag_mode = cur_tab == "Dragging On"
            other_tab = "Dragging Off" if drag_mode else "Dragging On" 
            # update drag button text and color 
            button_text= f"Drag Mode {'On' if drag_mode else 'Off'}"
            color = ('white', 'red') if drag_mode else ('black', 'green') # green is default 
            drag_button.update(text= button_text, button_color=color)
            # Want to disable user input and block focus when in drag mode -- should only be dragging objects. 
            user_input.update(disabled=drag_mode) # disabled in the off chance a user clicks in the area where it is - unlikely but still possible. 
            user_input.block_focus(block= drag_mode ) 
            # this creates the illusion that this all occurs within one canvas 
            window[cur_tab].update(visible=True)
            window[other_tab].update(visible=False)
            window[cur_tab].select() # select the cur tab we are now on 

        if event == "-CANVAS-": # main canvas 
            click_location = values[event] # update clicked location variable with where user clicked
            no_figures_at_location = True
            for figure in canvas.get_figures_at_location(click_location):
                # if there is a figure user is not trying to create a new textbox at this location --
                # they are selecting or deselecting an already present textbox at this location. 
                if figure in figures:
                    figures[figure]['selected'] = not figures[figure]['selected'] # toggle the selected value
                    is_selected = figures[figure]['selected']
                    # print(f"figure text = {figures[figure]['text']} figure selected = {is_selected}")
                    if is_selected:
                        # draw the selected-bounding-box
                        draw_bounding_box(canvas, figure, figures)

                    else:
                        # user deselected
                        remove_selected_bounding_box(figures, figure, canvas) 
                    
                    no_figures_at_location = False

            # we didnt find any figures at location -- user is trying to make new textbox there. 
            if no_figures_at_location: 
                user_input.update("") # clear the user input 
                user_input.set_focus() # trigger input event to get user input to draw text onto the canvas at this location 
            
        if event.startswith("-CANVAS-DRAG-"): # user is in drag mode 

            click_location = values["-CANVAS-DRAG-"] # update clicked location variable with where user clicked
            threshold = 20  # this is the 'error' value we give for a drag --> sort of like a hotspot 
            for figure in figures_on_drag_canvas.keys():
                # print(figure)
                figure_location = figures_on_drag_canvas[figure]["main-canvas-location"]
                figure_type = figures_on_drag_canvas[figure]["type"] 
                # print(figures_on_drag_canvas[figure]["text"])
                # print(f"Figure location for {figures_on_drag_canvas[figure]['text']}: {figure_location}. click loc: {click_location} ")
                fig_x, fig_y = figure_location
                click_x, click_y = click_location
                if abs(fig_x - click_x) <= threshold and abs(fig_y - click_y) <= threshold and figure_type == "text": # within our hotspot for dragging

                    if drag_hotspot:
                        canvas_with_drag.delete_figure(drag_hotspot)

                    drag_hotspot = canvas_with_drag.draw_circle(figure_location, radius=threshold)
                    # relocate drag canvas's text and bounding boxes 
                    drag_bounding_box = figures_on_drag_canvas[figure]["bounding-box"]
                    canvas_with_drag.relocate_figure(figure, click_x, click_y)
                    x, y = canvas_with_drag.get_bounding_box(figure)[0] # grab bounding box coordinates  from top left 
                    canvas_with_drag.relocate_figure(drag_bounding_box, x,y) 
                    # grab main canvas text and bounding boxes 
                    main_canvas_reference_figure = figures_on_drag_canvas[figure]["main-canvas-reference"]
                    bounding_box = figures[main_canvas_reference_figure]["bounding-box"] 
                    # whatever we do to the drag canvas needs to be reflected on our main canvas 
                    canvas.relocate_figure(main_canvas_reference_figure, click_x, click_y) # relocate the text 
                    canvas.relocate_figure(bounding_box, x, y) # relocate the texts bounding box using same coordinaes 
                    # update the main canvas location of that figure since we relocated it
                    figures_on_drag_canvas[figure]["main-canvas-location"] = click_location
                    # update lines 
                    update_lines(figure_location, click_location, figures, canvas, canvas_with_drag)

                
        if event == "-INPUT-": 
            # delete previously drawn figures at location on main canvas 
            delete_previous_drawn_figures(click_location, figures, canvas) 
            # do the same for the drag canvas 
            delete_previous_drawn_figures(click_location, figures_on_drag_canvas, canvas_with_drag) 
            # create new figures to draw at location on main canvas, the figures which are the user text and the corresponding bounding box. 
            text = values[event]
            draw_text_and_box_figures(
                text, click_location, font_size, canvas, figures,
                canvas_with_drag, figures_on_drag_canvas
                )

        
        if event == "-CONNECT-":
            # we don't need to check if correct amount 
            # of boxes have been selected as they couldn't 
            # trigger this event if that were not the case. 
            selected = get_selected_text_figures(figures)
            fig_and_loc_1, fig_and_loc2 = get_location_of_figures(selected, figures_on_drag_canvas)
            fig1, loc1, = fig_and_loc_1
            fig2, loc2 = fig_and_loc2
            # draw lines on each canvas 
            line_on_main = canvas.draw_line(loc1, loc2)
            line_on_drag = canvas_with_drag.draw_line(loc1, loc2)
            # send each line to the back on each canvas 
            canvas.send_figure_to_back(line_on_main) 
            canvas_with_drag.send_figure_to_back(line_on_drag)
            # delete selected bounding box for both figures 
            remove_selected_bounding_box(figures, fig1, canvas)
            remove_selected_bounding_box(figures, fig2, canvas)
            # turn selected property for each figure in figures dict to false 
            figures[fig1]['selected'] = False 
            figures[fig2]['selected'] = False 
            # create new property: line-reference to keep track of the line -- both figures will have it in both reference point dics
            figures[f"line-{line_count}"] = {
                                        "type":"line", 
                                        "locations": (loc1, loc2),
                                        "line-ids": (line_on_main, line_on_drag)  
                                    }
            line_count += 1 # increment line count 
        
        if event == "-DELETE-":
            selected_text_figs = get_selected_text_figures(figures)
            text_figs_on_drag = get_figures_on_drag_ids(selected_text_boxes, figures_on_drag_canvas)
            for i, text_figure in enumerate(selected_text_boxes):

                remove_selected_bounding_box(figures, text_figure, canvas)
                # delete text 
                canvas.delete_figure(text_figure)
                canvas_with_drag.delete_figure( text_figs_on_drag[i])
                # delete textbox 
                canvas.delete_figure(
                    figures[text_figure]['bounding-box'] 
                )
                canvas_with_drag.delete_figure(
                    figures_on_drag_canvas[ text_figs_on_drag[i] ]['bounding-box'] 
                )
                # get their locations to delete attached lines 
                location = figures_on_drag_canvas[ text_figs_on_drag[i] ]["main-canvas-location"] 
                lines = get_lines_at_location(location, figures)
                for line in lines:
                    line_id_main, line_id_drag = figures[line]["line-ids"]  
                    canvas.delete_figure(line_id_main)
                    canvas_with_drag.delete_figure(line_id_drag)
                    # delete line reference from figures dict 
                    del figures[line] 

                # delete text figure references from main canvas and drag canvas dictionaries 
                del figures[text_figure]
                del figures_on_drag_canvas[text_figs_on_drag[i]]

        # update button colors and visiblities after all events have occured
        # we do not want any of these to be enabled when in drag mode -- drag mode is strictly 
        # reserved for dragging events ! 
        selected_text_boxes = get_selected_text_figures(figures)
        window['-CONNECT-'].update(
            disabled = not len(selected_text_boxes) == 2, 
            button_color = ("black", "yellow") if len(selected_text_boxes) == 2  and cur_tab == "Dragging Off" else ("black", "grey") 
            )
        window['-DELETE-'].update(
            disabled = not len(selected_text_boxes) > 0, 
            button_color = ("white", "red") if len(selected_text_boxes) >0 and cur_tab == "Dragging Off" else ("black", "grey")
            ) 

    window.close() 
if __name__ == '__main__':
    main() 