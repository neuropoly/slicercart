import slicer
import vtk


# MB CODE BELOW: MOUSE CUSTOMIZATION CLASS
class CustomInteractorStyle(vtk.vtkInteractorStyleImage):
    def __init__(self, sliceWidget=None):
        """
        __init__

        Args:
            sliceWidget: Description of sliceWidget.
        """
        self.AddObserver("RightButtonPressEvent",
                         self.onRightButtonPressEvent)
        self.AddObserver("MouseMoveEvent", self.onMouseMoveEvent)
        self.AddObserver("RightButtonReleaseEvent",
                         self.onRightButtonReleaseEvent)
        self.AddObserver("MouseWheelForwardEvent",
                         self.onMouseWheelForwardEvent)
        self.AddObserver("MouseWheelBackwardEvent",
                         self.onMouseWheelBackwardEvent)
        self.AddObserver("LeftButtonPressEvent",
                         self.onLeftButtonPressEvent)
        self.AddObserver("LeftButtonReleaseEvent",
                         self.onLeftButtonReleaseEvent)
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)
        self.AddObserver("KeyReleaseEvent", self.onKeyReleaseEvent)
        self.startPosition = None
        self.sliceWidget = sliceWidget
        self.sliceNode = self.sliceWidget.mrmlSliceNode()
        self.sliceLogic = slicer.app.applicationLogic().GetSliceLogic(
            self.sliceNode)
        self.panning = False
        self.zooming = False
        self.adjustingWindowLevel = False
        self.z_pressed = False

    def onRightButtonPressEvent(self, obj, event):
        """
        onRightButtonPressEvent

        Args:
            obj: Description of obj.
            event: Description of event.
        """
        self.startPosition = self.GetInteractor().GetEventPosition()
        self.panning = True
        self.OnRightButtonDown()
        return

    def onMouseMoveEvent(self, obj, event):
        """
        onMouseMoveEvent

        Args:
            obj: Description of obj.
            event: Description of event.
        """
        if self.panning and self.startPosition:
            currentPosition = self.GetInteractor().GetEventPosition()
            deltaX = self.startPosition[0] - currentPosition[0]
            deltaY = self.startPosition[1] - currentPosition[1]

            # Adjust the image position based on mouse movement
            pan = self.sliceNode.GetXYZOrigin()
            self.sliceNode.SetXYZOrigin(pan[0] + deltaX, pan[1] + deltaY,
                                        pan[2])
            self.sliceNode.Modified()

            self.startPosition = currentPosition
        elif self.adjustingWindowLevel and self.startPosition:
            currentPosition = self.GetInteractor().GetEventPosition()
            deltaX = currentPosition[0] - self.startPosition[0]
            deltaY = self.startPosition[1] - currentPosition[1]

            # Adjust the window level and width based on mouse movement
            volumeNode = self.sliceLogic.GetBackgroundLayer().GetVolumeNode()
            displayNode = volumeNode.GetDisplayNode()
            currentWindowLevel = displayNode.GetLevel()
            currentWindowWidth = displayNode.GetWindow()

            newWindowLevel = currentWindowLevel + deltaY
            newWindowWidth = currentWindowWidth + deltaX

            displayNode.SetLevel(newWindowLevel)
            displayNode.SetWindow(newWindowWidth)

            self.startPosition = currentPosition

        elif self.zooming and self.startPosition:
            self.zoom()
            self.startPosition = self.GetInteractor().GetEventPosition()

        self.OnMouseMove()
        return

    def onRightButtonReleaseEvent(self, obj, event):
        """
        onRightButtonReleaseEvent

        Args:
            obj: Description of obj.
            event: Description of event.
        """
        self.startPosition = None
        self.panning = False
        self.OnRightButtonUp()
        return

    def onLeftButtonPressEvent(self, obj, event):
        """
        onLeftButtonPressEvent

        Args:
            obj: Description of obj.
            event: Description of event.
        """
        self.startPosition = self.GetInteractor().GetEventPosition()
        self.adjustingWindowLevel = True
        self.OnLeftButtonDown()
        return

    def onLeftButtonReleaseEvent(self, obj, event):
        """
        onLeftButtonReleaseEvent

        Args:
            obj: Description of obj.
            event: Description of event.
        """
        self.startPosition = None
        self.adjustingWindowLevel = False
        self.OnLeftButtonUp()
        return

    def onKeyPressEvent(self, obj, event):
        """
        onKeyPressEvent

        Args:
            obj: Description of obj.
            event: Description of event.
        """
        key = self.GetInteractor().GetKeySym()
        if key == "x":
            self.z_pressed = True
        self.OnKeyPress()
        return

    def onKeyReleaseEvent(self, obj, event):
        """
        onKeyReleaseEvent

        Args:
            obj: Description of obj.
            event: Description of event.
        """
        key = self.GetInteractor().GetKeySym()
        if key == "x":
            self.z_pressed = False
        self.OnKeyRelease()
        return

    def onMouseWheelForwardEvent(self, obj, event):
        """
        onMouseWheelForwardEvent

        Args:
            obj: Description of obj.
            event: Description of event.
        """
        if self.z_pressed:
            # print("Mouse scroll")
            self.zoom_in()
            # print("self zoom done")
        else:
            # Move to the next slice
            currentOffset = self.sliceLogic.GetSliceOffset()
            newOffset = currentOffset + self.getSliceSpacing()  # Move one
            # slice forward
            self.sliceLogic.SetSliceOffset(newOffset)
            self.OnMouseWheelForward()
        return

    def onMouseWheelBackwardEvent(self, obj, event):
        """
        onMouseWheelBackwardEvent

        Args:
            obj: Description of obj.
            event: Description of event.
        """
        if self.z_pressed:
            # print("Mouse scroll")
            self.zoom_out()
        else:
            # Move to the previous slice
            currentOffset = self.sliceLogic.GetSliceOffset()
            newOffset = currentOffset - self.getSliceSpacing()  # Move one
            # slice backward
            self.sliceLogic.SetSliceOffset(newOffset)
            self.OnMouseWheelBackward()
        return

    def zoom_in(self):
        """
        zoom_in

        Args:
        """
        fov = self.sliceNode.GetFieldOfView()
        self.sliceNode.SetFieldOfView(fov[0] * 0.9, fov[1] * 0.9, fov[2])
        self.sliceNode.Modified()

    def zoom_out(self):
        """
        zoom_out

        Args:
        """
        fov = self.sliceNode.GetFieldOfView()
        self.sliceNode.SetFieldOfView(fov[0] / 0.9, fov[1] / 0.9, fov[2])
        self.sliceNode.Modified()

    def zoom(self):
        """
        zoom

        Args:
        """
        if self.startPosition:
            fov = self.sliceNode.GetFieldOfView()
            currentPos = self.GetInteractor().GetEventPosition()
            deltaY = self.startPosition[1] - currentPos[1]
            factor = 1.01 if deltaY > 0 else 0.99
            zoomSpeed = 10
            factor = factor ** (abs(deltaY) / zoomSpeed)
            self.sliceNode.SetFieldOfView(fov[0] * factor, fov[1] * factor,
                                          fov[2])
            self.sliceNode.Modified()

    def getSliceSpacing(self):
        """
        getSliceSpacing

        Args:
        """
        volumeNode = self.sliceLogic.GetBackgroundLayer().GetVolumeNode()
        if volumeNode:
            spacing = volumeNode.GetSpacing()
            return spacing[2]  # Return the spacing along the Z-axis
        return 1.0  # Default spacing if volumeNode is not available
