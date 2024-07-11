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
        java.io.File file1 = null;
        // The following exception was thrown during execution in test generation
        try {
            org.apache.pulsar.functions.utils.FunctionCommon.downloadFromHttpUrl("", file1);
            org.junit.Assert.fail("Expected exception of type java.net.MalformedURLException; message: no protocol: ");
        } catch (java.net.MalformedURLException e) {
            // Expected exception.
        }
    }

    @Test
    public void test2() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test2");
        java.io.File file1 = null;
        // The following exception was thrown during execution in test generation
        try {
            org.apache.pulsar.functions.utils.FunctionCommon.downloadFromHttpUrl("hi!", file1);
            org.junit.Assert.fail("Expected exception of type java.net.MalformedURLException; message: no protocol: hi!");
        } catch (java.net.MalformedURLException e) {
            // Expected exception.
        }
    }
}

