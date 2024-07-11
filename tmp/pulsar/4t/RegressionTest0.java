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
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList5 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test2() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test2");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList5 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "hi!", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test3() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test3");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList5 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test4() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test4");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList5 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "hi!", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test5() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test5");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList5 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test6() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test6");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList5 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test7() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test7");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList5 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "hi!", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test8() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test8");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList5 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "hi!", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }
}

