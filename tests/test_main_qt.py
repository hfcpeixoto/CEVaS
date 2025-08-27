import sys
import pytest
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox
from PyQt5.QtCore import Qt

# Add the main application path to sys.path to allow import
sys.path.insert(0, '.') 
from main import VariableStarsApp, AboutDialog, PickStarDialog # Assuming main.py is in the root
from CEVaS.CEAAL import Star # For Star class if needed for mocking

import numpy as np
from PIL import Image

# Ensure a QApplication instance exists for tests
@pytest.fixture(scope="session")
def qapp_session(request):
    """Session-scoped QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def app_window(qtbot, qapp_session):
    """Create and show the main application window."""
    window = VariableStarsApp()
    qtbot.addWidget(window) # Add to qtbot for cleanup
    window.show() # Show the window
    assert window.isVisible()
    return window

def test_main_window_opens(app_window):
    """Test if the main window opens and has the correct title."""
    assert app_window is not None
    assert app_window.isVisible()
    assert "CEVaS (CEAAL Variable Stars) - PyQt5" in app_window.windowTitle()

def test_about_dialog_opens(qtbot, app_window):
    """Test if the About dialog opens when the 'About' menu action is triggered."""
    
    # Find the "About" action in the helpMenu
    about_action = None
    for action in app_window.helpMenu.actions():
        if "About" in action.text():
            about_action = action
            break
    
    assert about_action is not None, "Could not find 'About' action in the Help menu."

    # Use a context manager to check for the dialog opening
    with qtbot.waitSignal(app_window.aboutAction.triggered, timeout=1000): # Assuming aboutAction is the QAction instance
        app_window.aboutAction.trigger() # Trigger the action

    # Check if a QDialog is active (the AboutDialog)
    active_dialog = QApplication.activeModalWidget()
    assert isinstance(active_dialog, AboutDialog), "AboutDialog did not open or is not the active modal widget."
    
    # Clean up by closing the dialog
    if active_dialog:
        active_dialog.close()


@patch.object(Star, 'getAverageRelativeLuminance')
def test_evaluate_magnitude_logic_success(mock_get_lum, qtbot, app_window):
    """Test the core logic of evaluateMagnitude with mocked luminance values."""
    # Mock return values for getAverageRelativeLuminance
    # Star1, Star2, VarStar luminances
    mock_get_lum.side_effect = [0.8, 0.2, 0.5] # Example values

    # Set input magnitudes for comparison stars
    app_window.star1_magEdit.setText("10.0")
    app_window.star2_magEdit.setText("12.0")

    # Simulate that stars have been picked (so their imgArray would not be None)
    # This is important for the checks inside _evaluateRelativeLuminance
    app_window.star1.xPick = "10"
    app_window.star1.yPick = "10"
    app_window.star1.imgArray = np.array([1]) # Dummy non-None value
    
    app_window.star2.xPick = "20"
    app_window.star2.yPick = "20"
    app_window.star2.imgArray = np.array([1])

    app_window.varStar.xPick = "30"
    app_window.varStar.yPick = "30"
    app_window.varStar.imgArray = np.array([1])

    # Call the evaluation logic
    app_window.evaluateMagnitude()

    # Expected calculation:
    # star1Mag = 10.0, star2Mag = 12.0
    # star1Lum = 0.8, star2Lum = 0.2, varStarLum = 0.5
    # alpha = (12.0 - 10.0) / (0.2 - 0.8) = 2.0 / -0.6 = -3.333...
    # varStarMag = (-3.333...) * (0.5 - 0.8) + 10.0
    # varStarMag = (-3.333...) * (-0.3) + 10.0 = 1.0 + 10.0 = 11.0
    expected_mag = "11.00" 
    assert app_window.varStar_magLbl.text() == expected_mag
    mock_get_lum.assert_called() # Ensure the mocked method was called

@patch.object(Star, 'getAverageRelativeLuminance')
def test_evaluate_magnitude_zero_division(mock_get_lum, qtbot, app_window):
    """Test evaluateMagnitude when comparison stars have same luminance (division by zero)."""
    mock_get_lum.side_effect = [0.5, 0.5, 0.3] # Star1 and Star2 luminance are the same

    app_window.star1_magEdit.setText("10.0")
    app_window.star2_magEdit.setText("12.0")

    app_window.star1.xPick, app_window.star1.yPick, app_window.star1.imgArray = "1", "1", np.array([1])
    app_window.star2.xPick, app_window.star2.yPick, app_window.star2.imgArray = "1", "1", np.array([1])
    app_window.varStar.xPick, app_window.varStar.yPick, app_window.varStar.imgArray = "1", "1", np.array([1])
    
    # Patch QMessageBox.critical to check if it's called
    with patch('main.QMessageBox.critical') as mock_critical_msg:
        app_window.evaluateMagnitude()
        mock_critical_msg.assert_called_once()
        # Further check the message if needed:
        # args, _ = mock_critical_msg.call_args
        # assert "Relative luminance of comparison stars is too similar" in args[1]

def test_evaluate_magnitude_invalid_input(qtbot, app_window):
    """Test evaluateMagnitude with non-numeric input for magnitudes."""
    app_window.star1_magEdit.setText("invalid")
    app_window.star2_magEdit.setText("12.0")

    app_window.star1.xPick, app_window.star1.yPick, app_window.star1.imgArray = "1", "1", np.array([1])
    app_window.star2.xPick, app_window.star2.yPick, app_window.star2.imgArray = "1", "1", np.array([1])
    app_window.varStar.xPick, app_window.varStar.yPick, app_window.varStar.imgArray = "1", "1", np.array([1])

    with patch('main.QMessageBox.warning') as mock_warning_msg:
        app_window.evaluateMagnitude()
        mock_warning_msg.assert_called_once()
        args, _ = mock_warning_msg.call_args
        assert "Magnitudes for comparison stars must be valid numbers" in args[1]

def test_evaluate_magnitude_stars_not_picked(qtbot, app_window):
    """Test evaluateMagnitude when stars are not picked."""
    # Reset picks (default state)
    app_window.star1.xPick = "0"
    # ... (other stars also "0" by default)

    with patch('main.QMessageBox.warning') as mock_warning_msg:
        app_window.evaluateMagnitude()
        mock_warning_msg.assert_called_once()
        args, _ = mock_warning_msg.call_args
        assert "Please pick all three stars" in args[1]


# Test for image selection process
@patch('main.QFileDialog.getOpenFileName')
def test_image_selection_simulated(mock_get_open_file_name, qtbot, app_window):
    """Test the image selection process by simulating QFileDialog."""
    # Use an existing image in the repo for the test
    test_image_path = "./logo_ceaal_transp.png" 
    
    # Check if the test image actually exists to prevent test failure due to missing file
    try:
        with open(test_image_path, 'rb') as f:
            pass
    except FileNotFoundError:
        pytest.skip(f"Test image {test_image_path} not found. Skipping test_image_selection_simulated.")


    mock_get_open_file_name.return_value = (test_image_path, "Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif *.tif *.tiff);;All Files (*)")

    app_window.selectImage() # Call the method that uses the dialog

    assert app_window.pilImg is not None
    assert isinstance(app_window.pilImg, Image.Image)
    assert app_window.baseQtImg is not None
    assert not app_window.baseQtImg.isNull()
    assert app_window.filename == test_image_path
    assert test_image_path in app_window.statusBar.currentMessage()
    
    # Check if the scene has an item (the pixmap)
    assert len(app_window.imageScene.items()) > 0


@patch('main.QFileDialog.getSaveFileName')
@patch('builtins.open', new_callable=MagicMock)
def test_save_data_simulated(mock_open, mock_get_save_file_name, qtbot, app_window):
    """Test the save data process by simulating QFileDialog and file writing."""
    test_save_path = "dummy_save.csv"
    mock_get_save_file_name.return_value = (test_save_path, "CSV Files (*.csv)")

    # Populate some data to save
    app_window.filename = "test_image.tif"
    app_window.star1.xPick, app_window.star1.yPick = "10", "11"
    app_window.star1_magEdit.setText("10.5")
    app_window.star1.imgArray = np.array([1]) # To allow getAverageRelativeLuminance
    app_window.star2.xPick, app_window.star2.yPick = "20", "21"
    app_window.star2_magEdit.setText("12.5")
    app_window.star2.imgArray = np.array([1])
    app_window.varStar.xPick, app_window.varStar.yPick = "30", "31"
    app_window.varStar.magnitude = "11.50" # Calculated value
    app_window.varStar.imgArray = np.array([1])

    with patch.object(app_window.star1, 'getAverageRelativeLuminance', return_value=0.75), \
         patch.object(app_window.star2, 'getAverageRelativeLuminance', return_value=0.25), \
         patch.object(app_window.varStar, 'getAverageRelativeLuminance', return_value=0.50):
        
        with patch('main.QMessageBox.information') as mock_info_msg: # To suppress the dialog during test
            app_window.saveData()

    mock_get_save_file_name.assert_called_once()
    mock_open.assert_called_once_with(test_save_path, 'w')
    
    # Check what was written to the file (simplified check of handle().write() calls)
    handle = mock_open()
    # Example: check if header was written
    # This is a bit fragile as it depends on the exact string.
    # A more robust way would be to capture all .write() calls and parse the content.
    # For now, let's check if 'Image File:' was written
    
    # Get all write calls
    write_calls = [call_args[0][0] for call_args in handle.write.call_args_list]
    written_content = "".join(write_calls)
    
    assert "Image File: test_image.tif" in written_content
    assert "Star,xPick,yPick,Magnitude,RelativeLuminance" in written_content
    assert "Comparison Star 1,10,11,10.5,0.75" in written_content
    assert "Variable Star,30,31,11.50,0.5" in written_content
    
    mock_info_msg.assert_called_once() # Check if success message was queued
    
    # Clean up (not strictly necessary with mocks but good practice)
    app_window.filename = "No image selected." # Reset filename

# It might be good to add a test for PickStarDialog if its logic becomes complex,
# but for now, its main job is to get coordinates, which is indirectly tested by star picking.

# To run these tests:
# 1. Ensure pytest and pytest-qt are installed (pip install pytest pytest-qt)
# 2. Navigate to the root directory of the project in the terminal
# 3. Run `pytest`
# (You might need to `export PYTHONPATH=.` or similar depending on your setup if imports fail)

# If logo_ceaal_transp.png is crucial for AboutDialog visual testing (not done here),
# ensure it's available or mock its loading.
# The current AboutDialog test only checks if it opens.
# The image selection test uses it as a readily available image.
# The app icon loading in main.py also uses it.
# Make sure this file is in the root directory when tests are run or adjust path.
# For tests, it's often better to mock file system interactions.
# The test_image_selection_simulated uses the actual logo file.
# If this file is missing, the test will be skipped due to the check.
# This helps ensure tests don't fail due to missing non-critical assets if they are handled gracefully.
# The app icon loading in main.py itself has a print warning if the icon is not found.
# The AboutDialog also has a print warning.
# The tests/test_main_qt.py assumes it's run from the project root where logo_ceaal_transp.png exists.
# If running tests from within the tests/ directory, paths might need adjustment (e.g., "../logo_ceaal_transp.png").
# The sys.path.insert(0, '.') should handle imports correctly when running pytest from the root.
# The test for image selection uses "./logo_ceaal_transp.png" assuming pytest is run from the project root.
# The AboutDialog in main.py also uses "./logo_ceaal_transp.png".
# The app icon in main.py uses "./logo_ceaal_transp.png".
# Consistency in pathing from project root is key.
```
