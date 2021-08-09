import PySimpleGUI as sg

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

def main():
    sg.theme(sg.theme_list()[100])
    # Create widgets that will be in our window 
    # canvas is our main canvas which we do most of the drawing onto 
    canvas = sg.Graph((700,600), (0,0), (500, 500), enable_events=True, key='-CANVAS-', background_color="white")
    # we need a new canvas object to enable dragging 
    canvas_with_drag = sg.Graph((700,600), (0,0), (500, 500), enable_events=True, key='-CANVAS-DRAG-', drag_submits = True, background_color="white")
    # put each canvas element into their own seperate tabs -- we will only have one visible at a time in order to 
    # maintain the illusion that all this is occuring on the same canvas to the user 
    no_drag_tab = sg.Tab('Dragging Off', [[canvas]] )
    drag_tab = sg.Tab('Dragging On', [[canvas_with_drag]], visible=False) 
    tabs = sg.TabGroup([[no_drag_tab, drag_tab]]) 
    user_input = sg.Input('', key="-INPUT-", enable_events=True)
    drag_button = sg.Button('Drag Mode Off', key = "-DRAG-", button_color = ("black", "green"))
    # Build the final layout 
    layout = [[ user_input, drag_button], [tabs]  ]
    window = sg.Window('mimi 2', layout)
    # global variables 
    cur_tab = 'Dragging Off' # tracks the current tab the user is on -- changes when user goes in and out of drag mode 
    click_location = (50, 50) # tracks the last clicked location - chose an arbitrary location as a defuault loc to begin writing if user doesn't click before writing. 
    figures = {} # dictionary of figures drawn onto the canvas where key is their id (integer)
    figures_on_drag_canvas = {} # dictionary keeping track of figures drawn onto canvas where dragging is enabled ! 
    drag_hotspot = None # global variable so we can have a drag hotspot to help user see where the dragging hotspot is -- ie where they should distance their
    # text box from others within this radius! 
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break 
        if event == "-DRAG-":
            cur_tab = "Dragging Off" if cur_tab == "Dragging On" else "Dragging On" # toggle the current tab
            drag_mode = cur_tab == "Dragging On"
            other_tab = "Dragging Off" if drag_mode else "Dragging On" 
            # update drag button text and color 
            button_text= f"Drag Mode {'On' if drag_mode else 'Off'}"
            color = ('white', 'red') if drag_mode else ('black', 'green') # green is default 
            drag_button.update(text= button_text, button_color=color)
            # Want to disable user input when in drag mode -- should only be dragging objects. 
            user_input.update(disabled=drag_mode)
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
                        figures[figure]['selected-bounding-box'] = canvas.draw_rectangle(top_left, bott_right, line_color="green") 
                    else:
                        # user deselected
                        selected_bounding_box = figures[figure]['selected-bounding-box']
                        canvas.delete_figure( selected_bounding_box)
                        # remove the reference  
                        figures[figure]['selected-bounding-box'] = None 
                    
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
                
        if event == "-INPUT-": 
            # delete previously drawn figures at location on main canvas 
            delete_previous_drawn_figures(click_location, figures, canvas) 
            # do the same for the drag canvas 
            delete_previous_drawn_figures(click_location, figures_on_drag_canvas, canvas_with_drag) 
            # create new figures to draw at location on main canvas, the figures which are the user text and the corresponding bounding box. 
            text = values[event]
            new_text_id  = canvas.draw_text(text, click_location, text_location=sg.TEXT_LOCATION_LEFT)
            top_left, bott_right  = canvas.get_bounding_box(new_text_id)
            bounding_box_id = canvas.draw_rectangle(top_left, bott_right, line_color="red")
            # add newly drawn text id to figures dict
            figures[new_text_id] = {
                                    "type": "text",
                                    "text": text,
                                    "selected": False,
                                    "bounding-box":bounding_box_id, 
                                    "selected-bounding-box":None, # draw this when user selects this figure 
                                     }
            # create new figures to draw at location on drag canvas. We need these to be drawn so that when user goes 
            # into drag mode, these widgets will be present on the drag canvas when they move them. 
            new_text_id_drag = canvas_with_drag.draw_text(text, click_location, text_location=sg.TEXT_LOCATION_LEFT)
             # same location as on main canvas so need to re init top_left and bott_right variables 
            bounding_box_id_drag = canvas_with_drag.draw_rectangle(top_left, bott_right, line_color="red") 
            # add newly drawn text id to figures on drag canvas dict 
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


    window.close() 
if __name__ == '__main__':
    main() 