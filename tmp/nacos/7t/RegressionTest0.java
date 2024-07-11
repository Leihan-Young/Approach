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
        org.springframework.core.env.Environment environment0 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.Map<java.lang.String, java.lang.Object> strMap2 = com.alibaba.nacos.sys.utils.PropertiesUtil.getPropertiesWithPrefixForMap(environment0, "hi!");
            org.junit.Assert.fail("Expected exception of type java.lang.IllegalArgumentException; message: Object of class [null] must be an instance of interface org.springframework.core.env.ConfigurableEnvironment");
        } catch (java.lang.IllegalArgumentException e) {
            // Expected exception.
        }
    }

    @Test
    public void test2() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test2");
        org.springframework.core.env.Environment environment0 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.Map<java.lang.String, java.lang.Object> strMap2 = com.alibaba.nacos.sys.utils.PropertiesUtil.getPropertiesWithPrefixForMap(environment0, "");
            org.junit.Assert.fail("Expected exception of type java.lang.IllegalArgumentException; message: Object of class [null] must be an instance of interface org.springframework.core.env.ConfigurableEnvironment");
        } catch (java.lang.IllegalArgumentException e) {
            // Expected exception.
        }
    }
}

