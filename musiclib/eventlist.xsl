<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- $Id: eventlist.xsl,v 1.1 2022/09/13 00:41:05 dfm Exp $ -->
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
  <title>Event List</title>
  <style>
      .th { text-align: center; }
  </style>
</head>
<body>

<A NAME="top"></A>
<table border="1">
<caption><strong>Event List</strong></caption>
  <tr valign="center">
	<th><strong>When</strong></th>
	<th><strong>Where</strong></th>
  </tr>

  <xsl:for-each select="/eventlist/event">
  <xsl:sort select="@dtndx" />
  <tr>
    <td><xsl:value-of select="@when" /></td>
    <td><xsl:value-of select="@where" /></td>
   </tr>
  </xsl:for-each>
</table>

</body>
</html>
</xsl:template>
</xsl:stylesheet>
