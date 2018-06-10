from setuptools import setup

setup(
    name='app_tax',
    install_requires= [
        "requests",
        "flask",
        "selenium",
        "pymongo",
        "pillow"
    ],
    entry_points={
        'console_scripts' : [
            'app_tax = run_tax:main',
        ]
    }
)

'''
jekins构建脚本
echo "***************** start building *****************"
pyapp="/pyapp/app_tax"
workspace="/var/lib/jenkins/workspace/app_tax"
cd ${workspace}
buildout3 init
buildout3 bootstrap
mv -f  app/buildout.cfg  ./
bin/buildout
chmod +x stop.sh
./stop.sh
rm -rf ${pyapp}
cp -rf ${workspace} ${pyapp}
cd ${pyapp}/app/config
mv -f env_test.py env.py
cd ${pyapp}
chmod +x start.sh
./start.sh
echo "***************** end building *****************"
'''