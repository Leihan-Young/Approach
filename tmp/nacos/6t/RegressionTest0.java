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
        com.alibaba.nacos.core.cluster.Member member0 = null;
        com.alibaba.nacos.core.cluster.Member member1 = null;
        boolean boolean2 = com.alibaba.nacos.core.cluster.MemberUtil.isBasicInfoChanged(member0, member1);
        org.junit.Assert.assertTrue("'" + boolean2 + "' != '" + false + "'", boolean2 == false);
    }
}

