package gui;

import com.intellij.uiDesigner.core.GridConstraints;
import com.intellij.uiDesigner.core.GridLayoutManager;
import com.intellij.uiDesigner.core.Spacer;
import gui.util.GUIUtil;
import iot.Environment;
import iot.networkentity.Gateway;
import org.jxmapviewer.viewer.GeoPosition;
import util.MapHelper;

import util.Constants;

import javax.swing.*;
import java.awt.*;
import java.util.Random;

public class NewGatewayGUI {
    private JPanel mainPanel;
    private JTextField EUIDtextField;
    private JSpinner xPosSpinner;
    private JSpinner yPosSpinner;
    private JSpinner powerSpinner;
    private JSpinner SFSpinner;
    private JButton saveButton;
    private JButton generateButton;
    private JTextField LatitudeTextField;
    private JTextField LongitudeTextField;
    private Environment environment;

    private static final int DEFAULT_SEED = Constants.SEED;
    private Random random = new Random(DEFAULT_SEED);


    public NewGatewayGUI(Environment environment, GeoPosition geoPosition, JFrame frame, ConfigureGatewayPanel parent) {
        this.environment = environment;
        MapHelper mapHelper = environment.getMapHelper();

        xPosSpinner.setModel(new SpinnerNumberModel(mapHelper.toMapXCoordinate(geoPosition), 0, environment.getMaxXpos(), 1));
        yPosSpinner.setModel(new SpinnerNumberModel(mapHelper.toMapYCoordinate(geoPosition), 0, environment.getMaxYpos(), 1));
        powerSpinner.setModel(new SpinnerNumberModel(14, -3, 14, 1));
        SFSpinner.setModel(new SpinnerNumberModel(12, 1, 12, 1));
        generateNewEUID();
        updateLatLonFields();

        saveButton.addActionListener(e -> {
            environment.addGateway(new Gateway(Long.parseUnsignedLong(EUIDtextField.getText()),
                (int) xPosSpinner.getValue(), (int) yPosSpinner.getValue(),
                (int) powerSpinner.getValue(), (int) SFSpinner.getValue(),
                environment));
            parent.refresh();
            frame.dispose();
        });

        generateButton.addActionListener(e -> generateNewEUID());
        xPosSpinner.addChangeListener(e -> updateLonField());
        yPosSpinner.addChangeListener(e -> updateLatField());
    }

    private void generateNewEUID() {
        EUIDtextField.setText(Long.toUnsignedString(random.nextLong()));
    }


    private void updateLatLonFields() {
        updateLatField();
        updateLonField();
    }

    private void updateLatField() {
        GUIUtil.updateTextFieldCoordinate(LongitudeTextField, environment.getMapHelper().toLongitude((int) xPosSpinner.getValue()), "E", "W");
    }

    private void updateLonField() {
        GUIUtil.updateTextFieldCoordinate(LatitudeTextField, environment.getMapHelper().toLatitude((int) yPosSpinner.getValue()), "N", "S");
    }

    public JPanel getMainPanel() {
        return mainPanel;
    }

    {
// GUI initializer generated by IntelliJ IDEA GUI Designer
// >>> IMPORTANT!! <<<
// DO NOT EDIT OR ADD ANY CODE HERE!
        $$$setupUI$$$();
    }

    /**
     * Method generated by IntelliJ IDEA GUI Designer
     * >>> IMPORTANT!! <<<
     * DO NOT edit this method OR call it in your code!
     *
     * @noinspection ALL
     */
    private void $$$setupUI$$$() {
        mainPanel = new JPanel();
        mainPanel.setLayout(new GridLayoutManager(8, 6, new Insets(0, 0, 0, 0), -1, -1));
        mainPanel.setMinimumSize(new Dimension(600, 400));
        mainPanel.setPreferredSize(new Dimension(600, 400));
        final Spacer spacer1 = new Spacer();
        mainPanel.add(spacer1, new GridConstraints(0, 2, 1, 1, GridConstraints.ANCHOR_CENTER, GridConstraints.FILL_VERTICAL, 1, GridConstraints.SIZEPOLICY_WANT_GROW, null, null, null, 0, false));
        EUIDtextField = new JTextField();
        mainPanel.add(EUIDtextField, new GridConstraints(1, 2, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_HORIZONTAL, GridConstraints.SIZEPOLICY_WANT_GROW, GridConstraints.SIZEPOLICY_FIXED, null, new Dimension(150, -1), null, 0, false));
        final JLabel label1 = new JLabel();
        label1.setText("EUID");
        mainPanel.add(label1, new GridConstraints(1, 1, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_NONE, GridConstraints.SIZEPOLICY_FIXED, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        generateButton = new JButton();
        generateButton.setText("Generate");
        mainPanel.add(generateButton, new GridConstraints(1, 4, 1, 1, GridConstraints.ANCHOR_CENTER, GridConstraints.FILL_HORIZONTAL, GridConstraints.SIZEPOLICY_CAN_SHRINK | GridConstraints.SIZEPOLICY_CAN_GROW, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        final JLabel label2 = new JLabel();
        label2.setText("x-coordinate");
        mainPanel.add(label2, new GridConstraints(2, 1, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_NONE, GridConstraints.SIZEPOLICY_FIXED, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        xPosSpinner = new JSpinner();
        mainPanel.add(xPosSpinner, new GridConstraints(2, 2, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_HORIZONTAL, GridConstraints.SIZEPOLICY_WANT_GROW, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        final JLabel label3 = new JLabel();
        label3.setText("E");
        mainPanel.add(label3, new GridConstraints(2, 3, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_NONE, GridConstraints.SIZEPOLICY_FIXED, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        LatitudeTextField = new JTextField();
        LatitudeTextField.setEditable(false);
        mainPanel.add(LatitudeTextField, new GridConstraints(2, 4, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_HORIZONTAL, GridConstraints.SIZEPOLICY_WANT_GROW, GridConstraints.SIZEPOLICY_FIXED, null, new Dimension(100, -1), null, 0, false));
        final JLabel label4 = new JLabel();
        label4.setText("y-coordinate");
        mainPanel.add(label4, new GridConstraints(3, 1, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_NONE, GridConstraints.SIZEPOLICY_FIXED, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        yPosSpinner = new JSpinner();
        mainPanel.add(yPosSpinner, new GridConstraints(3, 2, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_HORIZONTAL, GridConstraints.SIZEPOLICY_WANT_GROW, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        final JLabel label5 = new JLabel();
        label5.setText("N");
        mainPanel.add(label5, new GridConstraints(3, 3, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_NONE, GridConstraints.SIZEPOLICY_FIXED, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        LongitudeTextField = new JTextField();
        LongitudeTextField.setEditable(false);
        mainPanel.add(LongitudeTextField, new GridConstraints(3, 4, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_HORIZONTAL, GridConstraints.SIZEPOLICY_WANT_GROW, GridConstraints.SIZEPOLICY_FIXED, null, new Dimension(100, -1), null, 0, false));
        final Spacer spacer2 = new Spacer();
        mainPanel.add(spacer2, new GridConstraints(3, 0, 1, 1, GridConstraints.ANCHOR_CENTER, GridConstraints.FILL_HORIZONTAL, GridConstraints.SIZEPOLICY_WANT_GROW, 1, null, null, null, 0, false));
        final Spacer spacer3 = new Spacer();
        mainPanel.add(spacer3, new GridConstraints(3, 5, 1, 1, GridConstraints.ANCHOR_CENTER, GridConstraints.FILL_HORIZONTAL, GridConstraints.SIZEPOLICY_WANT_GROW, 1, null, null, null, 0, false));
        final JLabel label6 = new JLabel();
        label6.setText("Powersetting");
        mainPanel.add(label6, new GridConstraints(4, 1, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_NONE, GridConstraints.SIZEPOLICY_FIXED, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        final JLabel label7 = new JLabel();
        label7.setText("Spreading factor");
        mainPanel.add(label7, new GridConstraints(5, 1, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_NONE, GridConstraints.SIZEPOLICY_FIXED, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        powerSpinner = new JSpinner();
        mainPanel.add(powerSpinner, new GridConstraints(4, 2, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_HORIZONTAL, GridConstraints.SIZEPOLICY_WANT_GROW, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        SFSpinner = new JSpinner();
        mainPanel.add(SFSpinner, new GridConstraints(5, 2, 1, 1, GridConstraints.ANCHOR_WEST, GridConstraints.FILL_HORIZONTAL, GridConstraints.SIZEPOLICY_WANT_GROW, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        saveButton = new JButton();
        saveButton.setText("Save");
        mainPanel.add(saveButton, new GridConstraints(6, 4, 1, 1, GridConstraints.ANCHOR_CENTER, GridConstraints.FILL_HORIZONTAL, GridConstraints.SIZEPOLICY_CAN_SHRINK | GridConstraints.SIZEPOLICY_CAN_GROW, GridConstraints.SIZEPOLICY_FIXED, null, null, null, 0, false));
        final Spacer spacer4 = new Spacer();
        mainPanel.add(spacer4, new GridConstraints(7, 4, 1, 1, GridConstraints.ANCHOR_CENTER, GridConstraints.FILL_VERTICAL, 1, GridConstraints.SIZEPOLICY_WANT_GROW, null, null, null, 0, false));
    }

    /**
     * @noinspection ALL
     */
    public JComponent $$$getRootComponent$$$() {
        return mainPanel;
    }

}
