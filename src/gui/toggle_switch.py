import tkinter as tk

class ToggleSwitch(tk.Canvas):
    def __init__(self, master,
                 width=80, height=40, padding=3,
                 on=False,
                 color_on="#34c759", color_off="#c7c7cc",
                 knob_color="white",
                 bg_color=None,
                 command=None):
        if bg_color is None:
            bg_color = master["bg"]
        super().__init__(master, width=width, height=height, highlightthickness=0, bg=bg_color)

        self.w, self.h, self.p = width, height, padding
        self.r = (height - 2*padding) // 2
        self.on = on
        self.command = command
        self.color_on = color_on
        self.color_off = color_off
        self.knob_color = knob_color
        self.knob_x_on  = width - padding - self.r*2
        self.knob_x_off = padding
        self.animating = False

        # Track pieces (rounded rectangle)
        self.track_left  = self.create_oval(padding, padding, padding+2*self.r, padding+2*self.r, width=0)
        self.track_mid   = self.create_rectangle(padding+self.r, padding, width-padding-self.r, height-padding, width=0)
        self.track_right = self.create_oval(width-padding-2*self.r, padding, width-padding, padding+2*self.r, width=0)

        # Knob
        self.knob = self.create_oval(0, padding, 0+2*self.r, padding+2*self.r, width=0)

        self.bind("<Button-1>", self._on_click)
        self._redraw(initial=True)

    def _color_track(self):
        return self.color_on if self.on else self.color_off

    def _redraw(self, initial=False):
        fill = self._color_track()
        for item in (self.track_left, self.track_mid, self.track_right):
            self.itemconfig(item, fill=fill)
        x = self.knob_x_on if self.on else self.knob_x_off
        self.coords(self.knob, x, self.p, x+2*self.r, self.p+2*self.r)
        self.itemconfig(self.knob, fill=self.knob_color)
        if (not initial) and self.command:
            self.command(self.on)

    def _on_click(self, _):
        if self.animating:
            return
        self._animate_to(not self.on)

    def _animate_to(self, target_on, frames=12):
        self.animating = True
        start = self.knob_x_on if self.on else self.knob_x_off
        end   = self.knob_x_on if target_on else self.knob_x_off
        dx = (end - start) / frames
        step = 0

        def tick():
            nonlocal step, start
            if step < frames:
                start += dx
                self.coords(self.knob, start, self.p, start+2*self.r, self.p+2*self.r)
                self.after(12, tick)
                step += 1
            else:
                self.on = target_on
                self.animating = False
                self._redraw()

        tick()


# Factory function
def create_toggle(parent,
                  width=80, height=40, padding=3,
                  on=False,
                  mode="light",
                  color_on=None, color_off=None,
                  knob_color=None,
                  command=None):
    """
    Creates a customizable toggle switch.

    Parameters:
      parent     : tk widget to attach
      width      : toggle width
      height     : toggle height
      padding    : inner padding
      on         : initial state
      mode       : "light" or "dark"
      color_on   : track color when ON
      color_off  : track color when OFF
      knob_color : knob color
      command    : callback(state: bool)
    """
    if mode == "light":
        default_on, default_off, default_knob, default_bg = "#34c759", "#c7c7cc", "white", parent["bg"]
    elif mode == "dark":
        default_on, default_off, default_knob, default_bg = "#0be881", "#485460", "#f1f2f6", parent["bg"]
    else:
        default_on, default_off, default_knob, default_bg = "#34c759", "#c7c7cc", "white", parent["bg"]

    return ToggleSwitch(
        parent,
        width=width, height=height, padding=padding,
        on=on,
        color_on=color_on or default_on,
        color_off=color_off or default_off,
        knob_color=knob_color or default_knob,
        bg_color=default_bg,
        command=command
    )
