function init(){
  var parser = new ol.format.WMTSCapabilities();

  fetch('https://opencache.statkart.no/gatekeeper/gk/gk.open_wmts?Version=1.0.0&service=wmts&request=getcapabilities').then(function(response) {
  return response.text();
  }).then(function(text) {
  var result = parser.read(text);
  var topo4 = ol.source.WMTS.optionsFromCapabilities(result, {
      // opacity: 0.7,
      layer: 'topo4',
      matrixSet: 'EPSG:3857'
  });

  var europa = ol.source.WMTS.optionsFromCapabilities(result, {
      // opacity: 0.7,
      layer: 'europa',
      matrixSet: 'EPSG:3857'
  });

  var layers = [
    new ol.layer.Group({
      title: 'Base Layers',
      openInLayerSwitcher: true,
      layers: [
        new ol.layer.Tile({
          title: 'OpenStreetMap',
          baseLayer: true,
          visible: false,
          // load OSM (a connector predefined in the API) as source:
          source: new ol.source.OSM()
        }),
        new ol.layer.Tile({
          source: new ol.source.WMTS(europa),
          baseLayer: true,
          visible:true,
          title: 'Europakart'
          })
        ]
    }),
    new ol.layer.Tile({
      source: new ol.source.WMTS(topo4),
      baseLayer: false,
      visible:true,
      title: 'Topografisk norgeskart 4'
    })
  ]
  

  var control = [
      new ol.control.MousePosition({
      // undefinedHTML: '&nbsp;',
      projection: 'EPSG:4326',
      coordinateFormat: function (coordinate) {
          return ol.coordinate.format(coordinate, '{x}, {y}', 4);
      }
      }),
      new ol.control.LayerSwitcher({
        tipLabel: 'Layers',
        useLegendGraphics: true,
        collapsed: true
      }),
      new ol.control.ScaleLine(),
      new ol.control.Attribution({
        collapsible: true,
      }),
      new ol.control.Zoom()
      // new ol.control.ZoomSlider(),   
      // new ol.control.ZoomToExtent({ extent: [-1814952.98, 7181338.12, 5865423.97, 6925860.91] }),
  ];
  var navMap = new ol.Map({
    layers: layers,
    controls: control,
    target: "map_container",
    attributions:false,
    view : new ol.View({
      center: ol.proj.fromLonLat([16.30, 66.0]),
      zoom: 4.7
      }) ,   //center coords and zoom level:
  });

  navMap.on('click', function (evt){
    // console.info(evt.pixel);
    // console.info(navMap.getPixelFromCoordinate(evt.coordinate));
    // console.info(ol.proj.toLonLat(evt.coordinate));
    var coords = ol.proj.toLonLat(evt.coordinate);
    // var coord_utm_33 = ol.proj.transform(evt.coordinate, 'EPSG:3857', 'EPSG:32633');
    // var lat_m = coord_utm_33[1];
    // var lon_m = coord_utm_33[0];

    window.lat = coords[1];
    window.lon = coords[0];
    console.info( "Latitude: " + lat + " Longitude: " + lon)
    document.getElementById("lat_lon").innerHTML = [lat.toFixed(4),lon.toFixed(4)];
    // document.getElementById("lon").innerHTML = lon.toFixed(4);
  // document.getElementById("button_download").setAttribute('href',"download/"+lat+"/"+lon);
    var oldUrl = document.referrer;
    document.getElementById("button_download").setAttribute('href',oldUrl+"/download/"+lat+"/"+lon);

  });

  // function downloadData(){
  //   alert(lat,lon)
  //   document.getElementById("button_download").addEventListener("click", window.location.href="https://gisedu.itc.utwente.nl/student/s2451573/arkwiz/download/"+lat+"/"+lon);
  // }
  // popup
  var popup = new ol.Overlay.Popup();
  navMap.addOverlay(popup);

  var geocoder = new Geocoder('nominatim', {
    provider: 'osm',
    lang: 'en',
    placeholder: 'Search for an address...',
    limit: 5,
    targetType: 'text-input',
    debug: false,
    autoComplete: true,
    keepOpen: false
  });
  navMap.addControl(geocoder);

  geocoder.on('addresschosen', function (evt) {
    var feature = evt.feature;
    var coords = ol.proj.toLonLat(evt.coordinate);
    window.lat = coords[1];
    window.lon = coords[0];
    geocoder.getSource().clear();
    geocoder.getSource().addFeature(feature);
    document.getElementById("lat_lon").innerHTML = [lat.toFixed(4),lon.toFixed(4)];
    // document.getElementById("lon").innerHTML = lon.toFixed(4);
    var oldUrl = document.referrer;
    document.getElementById("button_download").setAttribute('href',oldUrl+"/download/"+lat+"/"+lon);
    window.setTimeout(function () {
      popup.show(evt.coordinate, evt.address.formatted);
    }, 3000);
  })  

  });
}