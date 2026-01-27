<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- $Id: musiclib.xsl,v 1.1 2022/09/13 00:40:27 dfm Exp $ -->
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
<table border="1">
<caption><strong>Song List</strong></caption>
  <tr valign="center">
	<th><strong>Cat</strong></th>
	<th><strong>Name</strong></th>
  </tr>

  <xsl:for-each select="/musiclib/song">
  <xsl:sort select="category" />
  <xsl:sort select="@name" />
  <tr>
    <td><xsl:value-of select="category" /></td>
    <td><xsl:value-of select="@name" /></td>
   </tr>
  </xsl:for-each>
</table>

</body>
</html>
</xsl:template>
</xsl:stylesheet>
