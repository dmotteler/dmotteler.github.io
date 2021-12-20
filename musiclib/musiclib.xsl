<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0"
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="*">
   <xsl:apply-templates/>
</xsl:template>

<xsl:template match="text()">
   <xsl:value-of select="."/>
</xsl:template>

<xsl:template match="/">
<html>
<head> 
  <title>Song List</title>
  <style>
      .th { text-align: center; }
  </style>
</head>
<body>

<A NAME="top"></A>
<TABLE border="1">
<caption><STRONG>Song List</STRONG></caption>
  <tr valign="center">
	<th><STRONG>Key</STRONG></th>
	<th><STRONG>Categories</STRONG></th>
	<th><STRONG>Title</STRONG></th>
	<th><STRONG>Words</STRONG></th>
  </tr>

  <xsl:for-each select="/musiclib/song">
  <xsl:sort select="@name" />
  <tr>
    <td><xsl:value-of select="key" /></td>
    <td><xsl:value-of select="categories" /></td>
    <td><xsl:value-of select="@name" /></td>
    <td><xsl:value-of select="words" /></td>
   </tr>
  </xsl:for-each>
</TABLE>

</body>
</html>
</xsl:template>
</xsl:stylesheet>
