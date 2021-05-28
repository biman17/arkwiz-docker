from flask import Flask, send_file, abort, render_template, jsonify,redirect
from flask_cors import CORS
from osgeo import gdal
import os,sys
from shapely.geometry import Point
from shapely.ops import transform
from pyproj import Transformer, CRS
import requests
import logging
import shutil

app = Flask(__name__, template_folder='template')
CORS(app)


@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/download/<float:lat>/<float:lon>', methods = ["GET","POST"]) 

def get_data(lon, lat):   
    
    def download_file(url,local_filename):
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
        return local_filename # Variable with type filter. Accept only int

    print(sys.version)  
    print('GDAL:::',gdal.VersionInfo())
    lon_var=lon
    lat_var=lat
    # lat_var= 62.45845155668787  
    # lon_var=6.267915932047673
    print (lon_var, lat_var)
    aoi_point = Point(lon_var, lat_var)
    wgs84 = CRS('EPSG:4326')
    utm = CRS('EPSG:25833')

    transformer = Transformer.from_crs(wgs84, utm, always_xy=True).transform
    aoi_utm = Point(transformer(lon_var,lat_var))
    print('UTM coords::::', aoi_utm.coords.xy)

    #
    near_buf = aoi_utm.buffer(500, cap_style=3)
    far_buff = aoi_utm.buffer(20000, cap_style=3)
    near_extent = near_buf.bounds
    far_extent = far_buff.bounds
    bound_near = '{}%2C{}%2C{}%2C{}'.format(near_extent[0],near_extent[1],near_extent[2],near_extent[3])
    print('Bound_Near',bound_near)
    bound_far = '{}%2C{}%2C{}%2C{}'.format(far_extent[0],far_extent[1],far_extent[2],far_extent[3])
    print('Bound_Far',bound_far)

    root = r'datset_download\temp'
    filename = root
    # filename = os.path.join(root,str(lat_var).replace('.', '_')+'_'+str(lon_var).replace('.', '_'))

    if not os.path.isdir(filename):
        os.makedirs(filename)

    logging.basicConfig(level=logging.INFO,filename=os.path.join(filename,"Error_logs.txt"),filemode="w",format="%(asctime)-15s %(levelname)-8s %(message)s")

    download_dict = {}

    url_sr16_far = 'https://wms.nibio.no/cgi-bin/sr16?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&FORMAT=image%2Fpng&TRANSPARENT=true&LAYERS=SRRTRESLAG&CRS=EPSG%3A25833&WIDTH=4096&HEIGHT=4096&BBOX='+bound_far
    print('url_sr16_far:::::',url_sr16_far)
    url_sr16_near = 'https://wms.nibio.no/cgi-bin/sr16?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&FORMAT=image%2Fpng&TRANSPARENT=true&LAYERS=SRRTRESLAG&CRS=EPSG%3A25833&WIDTH=4096&HEIGHT=4096&BBOX='+bound_near
    print('url_sr16_near:::::',url_sr16_near)
    url_sr16_legend = 'https://wms.nibio.no/cgi-bin/sr16?language=nor&version=1.3.0&service=WMS&request=GetLegendGraphic&sld_version=1.1.0&layer=SRRTRESLAG&format=image/png&STYLE=default'
    print('url_sr16_legend:::::',url_sr16_legend)
    fname_sr16_far = os.path.join(filename,'sr16_far.png')
    fname_sr16_near = os.path.join(filename,'sr16_near.png')
    fname_sr16_legend = os.path.join(filename,'sr16_legend.png')

    url_ar50_far = 'https://wms.nibio.no/cgi-bin/ar50?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&FORMAT=image%2Fpng&TRANSPARENT=true&LAYERS=Treslag&CRS=EPSG%3A25833&WIDTH=4096&HEIGHT=4096&BBOX='+bound_far
    print('url_ar50_far:::::',url_ar50_far)
    url_ar50_near = 'https://wms.nibio.no/cgi-bin/ar50?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&FORMAT=image%2Fpng&TRANSPARENT=true&LAYERS=Treslag&CRS=EPSG%3A25833&WIDTH=4096&HEIGHT=4096&BBOX='+bound_near
    print('url_ar50_near:::::',url_ar50_near)
    url_ar50_legend = 'https://wms.nibio.no/cgi-bin/ar50?language=nor&version=1.3.0&service=WMS&request=GetLegendGraphic&sld_version=1.1.0&layer=TRESLAG&format=image/png&STYLE=default'
    print('url_ar50_legend:::::',url_ar50_legend)
    fname_ar50_far = os.path.join(filename,'ar50_far.png')
    fname_ar50_near = os.path.join(filename,'ar50_near.png')
    fname_ar50_legend = os.path.join(filename,'ar50_legend.png')



    # url_s2_far = 'https://openwms.statkart.no/skwms1/wms.sentinel2?service=WMS&request=GetMap&version=1.3.0&format=image%2Fpng&layers=sentinel2&CRS=EPSG%3A25833&WIDTH=4096&HEIGHT=4096&BBOX='+bound_far
    # print('URL S2 Far::::  ', url_s2_far)
    url_ortho_near = 'https://wms.geonorge.no/skwms1/wms.nib?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=ortofoto&SRS=EPSG:25833&Format=image%2Fpng&BBOX='+bound_near.replace('%2C', ',')+'&WIDTH=2048&HEIGHT=2048'
    print('url_ortho_near::::::',url_ortho_near)
    url_ortho_far = 'https://wms.geonorge.no/skwms1/wms.nib?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=ortofoto&SRS=EPSG:25833&Format=image%2Fpng&BBOX='+bound_far.replace('%2C', ',')+'&WIDTH=2048&HEIGHT=2048'
    print('url_ortho_far::::::',url_ortho_far)
    fname_s2_far = os.path.join(filename,'s2_far.png')
    fname_ortho_near = os.path.join(filename, 'ortho_near.png')
    fname_ortho_far = os.path.join(filename, 'ortho_far.png')

    wms_translate = gdal.TranslateOptions(format = 'PNG', width=4096, height=4096) #creationOptions=['BLOCKXSIZE=256', 'BLOCKYSIZE=256']
    wms_translate_near = gdal.TranslateOptions(format = 'PNG', width=2048, height=2048) #creationOptions=['BLOCKXSIZE=256', 'BLOCKYSIZE=256']

    base_url_s2 = "WMS:https://openwms.statkart.no/skwms1/wms.sentinel2?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=2020&SRS=EPSG:25833&TILESIZE=128&Format=image%2Fpng&WIDTH=4096&HEIGHT=4096&BBOX="
    s2_source_far = base_url_s2+bound_far.replace('%2C', ',')
    print('S2_source_far::::::',s2_source_far)
    s2_ds = gdal.Translate(fname_s2_far, s2_source_far, options = wms_translate)
    del s2_ds
    # base_url_ortho = "WMS:https://wms.geonorge.no/skwms1/wms.nib?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=ortofoto&SRS=EPSG:25833&TILESIZE=128&Format=image%2Fpng&BBOX="
    # ortho_source_far = base_url_ortho+bound_far.replace('%2C', ',')+'&WIDTH=2048&HEIGHT=2048'
    # ortho_source_near = base_url_ortho+bound_near.replace('%2C', ',')+'&WIDTH=2048&HEIGHT=2048'
    # print('Ortho_source_far::::::',ortho_source_far)
    # print('Ortho_source_near::::::',ortho_source_near)
    # ortho_ds_near = gdal.Translate(fname_ortho_near, ortho_source_near, options = wms_translate_near)
    # ortho_ds_far = gdal.Translate(fname_ortho_far, ortho_source_far, options = wms_translate_near)

    # del(ortho_ds_far,ortho_ds_near)
    # print(os.system('tree /F'))
    
    
    # url_dtm_near =  'https://wcs.geonorge.no/skwms1/wcs.dtm?service=wcs&request=getcoverage&version=2.0.1&coverageid=land_utm33_10m&int=bilinear&format=image%2Ftiff&subset=Long({},{})&subset=Lat({},{})'.format(near_extent[0],near_extent[2],near_extent[1],near_extent[3])
    url_dtm_near = "WCS:https://wms.geonorge.no/skwms1/wcs.hoyde-dtm1_33?version=1.0.0&coverage=1"    
    wcs_opt_near = gdal.TranslateOptions(format='GTiff',projWin=[near_extent[0],near_extent[3],near_extent[2],near_extent[1]])
    # wcs_opt_far = gdal.TranslateOptions(format='GTiff', outputType=gdal.GDT_UInt16, scaleParams=[[0, 3000,0, 65535]], projWin=[far_extent[0],far_extent[3],far_extent[2],far_extent[1]])
    # url_dtm_far = "WCS:https://wcs.geonorge.no/skwms1/wcs.dtm?VERSION=1.0.0&COVERAGE=land_utm33_10m"
    url_dtm_far =  'https://wcs.geonorge.no/skwms1/wcs.dtm?service=wcs&request=getcoverage&version=2.0.1&coverageid=land_utm33_10m&int=bilinear&format=image%2Ftiff&subset=Long({},{})&subset=Lat({},{})'.format(far_extent[0],far_extent[2],far_extent[1],far_extent[3])
    print('url_dtm_far:::::',url_dtm_far)
    fname_dtm_far = os.path.join(filename,'dtm_far.tif')
    fname_dtm_near = os.path.join(filename, 'dtm_near.tif')
        
    ds_wcs_near = gdal.Translate(fname_dtm_near, url_dtm_near, options = wcs_opt_near)   
    # del ds_wcs_near
    # ds_wcs_far = gdal.Translate(fname_dtm_far, url_dtm_far, options = wcs_opt_far)
    

    
    download_dict[url_sr16_far] = fname_sr16_far
    download_dict[url_sr16_near] = fname_sr16_near
    download_dict[url_sr16_legend] = fname_sr16_legend
    download_dict[url_ar50_far] = fname_ar50_far
    download_dict[url_ar50_near] = fname_ar50_near
    download_dict[url_ar50_legend] = fname_ar50_legend
    # download_dict[url_s2_far] = fname_s2_far
    download_dict[url_ortho_far] = fname_ortho_far
    download_dict[url_ortho_near] = fname_ortho_near
    # download_dict[url_dtm_near] = fname_dtm_near
    download_dict[url_dtm_far] = fname_dtm_far

    for i in download_dict.keys():
        try:
            # if not os.path.isfile(download_dict[i]):
            print(i)
            download_file(i, download_dict[i])
        except Exception as e:
            logging.info(e)
    
    ds_far = gdal.Open(fname_dtm_far)
    print(os.system('tree /F'))
    
    ds_near_16 = gdal.Translate(' ', srcDS=ds_wcs_near,  format = "Mem", outputType= gdal.GDT_UInt16,scaleParams=[[0, 3000,0, 65535]])
    ds_far_16 = gdal.Translate(' ', srcDS=ds_far,  format = "Mem", outputType= gdal.GDT_UInt16,scaleParams=[[0, 3000,0, 65535]])
    translate_options = gdal.TranslateOptions(format = 'PNG', width=4096, height=4096, outputType=gdal.GDT_UInt16)
    out_far = gdal.Translate(fname_dtm_far[:-3]+'png', ds_far_16, options = translate_options )
    out_near= gdal.Translate(fname_dtm_near[:-3]+'png', ds_near_16, options = translate_options)
    
    del(ds_wcs_near,ds_near_16,out_near,out_far)
    try:        
        os.remove(fname_dtm_far[:-4]+'.png.aux.xml')
        os.remove(fname_dtm_near[:-4]+'.png.aux.xml')
        os.remove(fname_ortho_far+'.aux.xml')
        os.remove(fname_ortho_near+'.aux.xml')
        os.remove(fname_s2_far+'.aux.xml')  
    except FileNotFoundError:
        pass
        
    

    zipfname = shutil.make_archive(filename, 'zip', filename)
            
    
    
    try:
        return send_file(zipfname, as_attachment=True)
    except FileNotFoundError:
        abort(404)
    
    
    logging.shutdown()
    # return jsonify({'Message':'File should be downloaded in root directory of server:: {}'.format(zipfname)})
    # return redirect("https://www.arkwiz.no/", code=302)
    # return '<html><head></head><body> <p> File should be downloaded in root directory of server:: {}</p> <a><p> Redirect back to <a href="http://localhost:8080/arkwiz/">Home</a> </p></body></html>'.format(zipfname)
    # return redirect("http://localhost:8080/arkwiz/", code=302)



if __name__ == '__main__':
#    app.run(debug=True)  # Enable reloader and debugger
    app.run(host='0.0.0.0',port = 80, debug=False)  # Enable reloader and debugger
#    app.run( host='10.61.62.207', port=5443,debug=True)  # Enable reloader and debugger

    