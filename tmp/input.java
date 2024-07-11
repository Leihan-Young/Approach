@Test
public void testGetConsumerKeyHashRanges() throws BrokerServiceException.ConsumerAssignException
{
    ConsistentHashingStickyKeyConsumerSelector selector = new ConsistentHashingStickyKeyConsumerSelector(3);
    List<String> consumerName = Arrays.asList("consumer1", "consumer2", "consumer3");
    List<Consumer> consumers = new ArrayList<>();
    for (String s : consumerName) {
        Consumer consumer = mock(Consumer.class);
        when(consumer.consumerName()).thenReturn(s);
        selector.addConsumer(consumer);
        consumers.add(consumer);
    }

    // Verify the hash ranges for each consumer
    for (Consumer consumer : consumers) {
        List<Range> ranges = selector.getConsumerKeyHashRanges().get(consumer);
        Assert.assertNotNull(ranges);
        Assert.assertEquals(3, ranges.size());
        // Add more assertions here to check the content and order of the ranges
    }
}
