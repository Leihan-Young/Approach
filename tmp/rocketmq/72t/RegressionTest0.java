import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class RegressionTest0 {

    public static boolean debug = false;

    @Test
    public void test1() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test1");
        // The following exception was thrown during execution in test generation
        try {
            java.lang.String str1 = org.apache.rocketmq.common.KeyBuilder.parseGroup("");
            org.junit.Assert.fail("Expected exception of type java.lang.StringIndexOutOfBoundsException; message: String index out of range: -7");
        } catch (java.lang.StringIndexOutOfBoundsException e) {
            // Expected exception.
        }
    }

    @Test
    public void test2() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test2");
        // The following exception was thrown during execution in test generation
        try {
            java.lang.String str1 = org.apache.rocketmq.common.KeyBuilder.parseGroup("hi!");
            org.junit.Assert.fail("Expected exception of type java.lang.StringIndexOutOfBoundsException; message: String index out of range: -4");
        } catch (java.lang.StringIndexOutOfBoundsException e) {
            // Expected exception.
        }
    }
}

