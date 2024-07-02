@Test
void read() {
    List<String> resourceNameList = ClasspathResourceDirectoryReader.read(getClass().getClassLoader(), "yaml").collect(Collectors.toList());
    assertThat(resourceNameList.size(), is(4));
    final String separator = File.separator;
    assertThat(resourceNameList, hasItems("yaml" + separator + "accepted-class.yaml", "yaml" + separator + "customized-obj.yaml", "yaml" + separator + "empty-config.yaml",
            "yaml" + separator + "shortcuts-fixture.yaml"));
}
