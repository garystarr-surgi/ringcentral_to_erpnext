from setuptools import setup, find_packages

setup(
    name="ringcentral_to_erpnext",
    version="1.0.0",
    description="RingCentral telephony integration for Frappe CRM / ERPNext",
    author="SurgiShop",
    author_email="gary@surgishop.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    package_data={
        "ringcentral_to_erpnext": [
            "**/*.json",
            "**/*.txt",
            "**/*.html",
            "**/*.js",
            "**/*.css",
        ]
    },
    install_requires=["requests>=2.28.0"],
)
