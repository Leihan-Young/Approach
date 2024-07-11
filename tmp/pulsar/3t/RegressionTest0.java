import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class RegressionTest0 {

    public static boolean debug = false;

    @Test
    public void test01() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test01");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "hi!", "", "hi!", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test02() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test02");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "hi!", "", "", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test03() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test03");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "hi!", "", "", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test04() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test04");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "", "", "", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test05() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test05");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "", "hi!", "hi!", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test06() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test06");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "hi!", "hi!", "", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test07() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test07");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "hi!", "", "", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test08() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test08");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "hi!", "hi!", "hi!", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test09() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test09");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "", "hi!", "", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test10() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test10");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "", "", "hi!", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test11() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test11");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "hi!", "", "hi!", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test12() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test12");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "", "", "hi!", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test13() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test13");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "", "hi!", "", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test14() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test14");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "hi!", "hi!", "hi!", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test15() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test15");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "hi!", "hi!", "", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test16() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test16");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "", "", "", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test17() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test17");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "hi!", "hi!", "", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test18() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test18");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "", "hi!", "hi!", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test19() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test19");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "", "", "hi!", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test20() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test20");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "hi!", "", "", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test21() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test21");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "", "hi!", "", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test22() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test22");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "", "", "", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test23() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test23");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "", "hi!", "hi!", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test24() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test24");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "hi!", "", "hi!", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test25() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test25");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "", "", "", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test26() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test26");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "", "", "hi!", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test27() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test27");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "hi!", "hi!", "hi!", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test28() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test28");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "hi!", "hi!", "", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test29() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test29");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "", "hi!", "hi!", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test30() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test30");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "hi!", "hi!", "hi!", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test31() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test31");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "", "hi!", "", "hi!", true);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }

    @Test
    public void test32() throws Throwable {
        if (debug)
            System.out.format("%n%s%n", "RegressionTest0.test32");
        org.apache.pulsar.functions.instance.InstanceConfig instanceConfig0 = null;
        org.apache.pulsar.functions.instance.AuthenticationConfig authenticationConfig1 = null;
        // The following exception was thrown during execution in test generation
        try {
            java.util.List<java.lang.String> strList7 = org.apache.pulsar.functions.runtime.RuntimeUtils.getGoInstanceCmd(instanceConfig0, authenticationConfig1, "hi!", "", "hi!", "", false);
            org.junit.Assert.fail("Expected exception of type java.lang.NullPointerException; message: Cannot invoke \"org.apache.pulsar.functions.instance.InstanceConfig.getClusterName()\" because \"instanceConfig\" is null");
        } catch (java.lang.NullPointerException e) {
            // Expected exception.
        }
    }
}

