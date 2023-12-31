package datagenerator.rangedsensor.pm10sensor;

import datagenerator.rangedsensor.api.RangeValue;

import java.util.Random;

import util.Constants;

public enum PM10Level implements RangeValue {

    VERY_LOW(0, 25),
    LOW(25, 50),
    MEDIUM(50, 90),
    HIGH(90, 180),
    VERY_HIGH(180, 255);

    private static final int DEFAULT_SEED = Constants.SEED;

    private final int lowerBound;
    private final int upperBound;
    private final Random random = new Random(DEFAULT_SEED);

    PM10Level(int lowerBound, int upperBound) {
        this.lowerBound = lowerBound;
        this.upperBound = upperBound;
    }

    @Override
    public int getLowerBound() {
        return lowerBound;
    }

    @Override
    public int getUpperBound() {
        return upperBound;
    }

    @Override
    public byte[] getValue() {
        return new byte[] { (byte) (getLowerBound() + random.nextInt(getUpperBound()-getLowerBound()))};
    }
}
