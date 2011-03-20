%define my_target_cpu %{_target_cpu}

%define subver 1.9
%define rubyver 1.9.2
%define patchversion p180

Summary:	Object Oriented Script Language
Name:		ruby%{subver}
Version:	%{rubyver}
Release: 	1%{?dist}

License:	Ruby or GPLv2
URL:		http://www.ruby-lang.org/
Group:		Development/Ruby
Source0:	ftp://ftp.ruby-lang.org/pub/ruby/1.9/ruby-1.9.2-p180.tar.gz
Source1:	rubyfaqall.html.bz2
Source2:	ProgrammingRuby-0.4.tar.bz2
Source3:	ruby.macros
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires:	autoconf
BuildRequires:	byacc
BuildRequires:	ncurses-devel
BuildRequires:	readline-devel
BuildRequires:	tcl-devel tk-devel
BuildRequires:	db4-devel
BuildRequires:  libgdbm-devel >= 1.8.3
BuildRequires:  openssl-devel
BuildRequires:	zlib1-devel

Provides:	/usr/bin/ruby%{subver}


%description
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl).  It is simple, straight-forward, and extensible.


%package	doc
Summary:	Documentation for the powerful language Ruby
Group:		Development/Ruby


%description	doc
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl). It is simple, straight-forward, and extensible.

This package contains the Ruby's documentation


%package	devel
Summary:	Development file for the powerful language Ruby
Group:		Development/Ruby
Requires:	%{name} = %{version}


%description	devel
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl). It is simple, straight-forward, and extensible.

This package contains the Ruby's devel files.


%package	tcltk
Summary:	Tk extension for the powerful language Ruby
Group:		Development/Ruby
Requires:	%{name} = %{version}


%description	tcltk
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl). It is simple, straight-forward, and extensible.

This package contains the Tk extension for Ruby.


%prep
%setup -q -n ruby-%{rubyver}-%{patchversion}


%build
echo '.text' | gcc -shared -o libdummy.so.0 -xassembler - -ltcl -ltk >& /dev/null && {
  if %{_bindir}/ldd libdummy.so.0 | grep -q "lib\(tcl\|tk\).so"; then
    echo "Your tcl/tk is broken, get one with versioning in the libraries."
    exit 1
  fi
  rm -f libdummy.so.0
}

CFLAGS=`echo %optflags | sed 's/-fomit-frame-pointer//'`
%configure --enable-shared --disable-rpath --enable-pthread \
	--with-ruby-version=minor --program-suffix=%{subver} \
	--with-sitedir=%_prefix/lib/%{name}/site_ruby \
	--with-vendordir=%_prefix/lib/%{name}/vendor_ruby \
	--with-old-os=linux-gnu

make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install install-doc

install -d %buildroot%{_docdir}/%{name}-%{version}
cp -a COPYING* ChangeLog README* ToDo sample %buildroot%{_docdir}/%{name}-%{version}
bzcat %{SOURCE1} > %buildroot%{_docdir}/%{name}-%{version}/FAQ.html

install -d %buildroot%{_datadir}/emacs/site-lisp
cp -a misc/ruby-mode.el %buildroot%{_datadir}/emacs/site-lisp

install -d %buildroot%{_sysconfdir}/emacs/site-start.d
cat <<EOF >%buildroot%{_sysconfdir}/emacs/site-start.d/%{name}.el
(autoload 'ruby-mode "ruby-mode" "Ruby editing mode." t)
(add-to-list 'auto-mode-alist '("\\\\.rb$" . ruby-mode))
(add-to-list 'interpreter-mode-alist '("ruby" . ruby-mode))
EOF

(cd %buildroot%{_docdir}/%{name}-%{version} ; tar xfj %{SOURCE2} ; cd Pro*; mv -f html/* . ; rm -rf html xml)

# Make the file/dirs list, filtering out tcl/tk and devel files
( cd %buildroot \
  && find usr/%{_lib}/ruby/%{subver} \
          \( -not -type d -printf "/%%p\n" \) \
          -or \( -type d -printf "%%%%dir /%%p\n" \) \
) | egrep -v '/(tcl)?tk|(%{my_target_cpu}-%{_target_os}/.*[ha]$)' > %{name}.list

# Fix scripts permissions and location
find %buildroot sample -type f | file -i -f - | grep text | cut -d: -f1 >text.list
cat text.list | xargs chmod 0644
#  Magic grepping to get only files with '#!' in the first line
cat text.list | xargs grep -n '^#!' | grep ':1:#!' | cut -d: -f1 >shebang.list
cat shebang.list | xargs sed -i -e 's|/usr/local/bin|/usr/bin|; s|\./ruby|/usr/bin/%{name}|'
cat shebang.list | xargs chmod 0755


# Install the rpm macros 
mkdir -p %buildroot%{_sysconfdir}/rpm/macros.d
cp %{SOURCE3} %buildroot%{_sysconfdir}/rpm/macros.d/%name.macros


%check
make test


%clean
rm -rf %{buildroot}


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig


%files -f %{name}.list
%defattr(-, root, root)
%dir %{_docdir}/%{name}-%{version}
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*
%{_docdir}/ruby1.9-1.9.2/README
%{_sysconfdir}/rpm/macros.d/%{name}.macros
%{_bindir}/*
%{_libdir}/libruby.so.*
%{_prefix}/lib/%{name}/site_ruby
%{_prefix}/lib/%{name}/gems/*
%{_mandir}/*/*
%{_datadir}/emacs/site-lisp/*


%files doc
%defattr(-, root, root)
%{_datadir}/ri*
%{_docdir}/%{name}-%{version}/COPYING*
%{_docdir}/%{name}-%{version}/ChangeLog
%{_docdir}/%{name}-%{version}/README.*
%{_docdir}/%{name}-%{version}/FAQ.html
%{_docdir}/%{name}-%{version}/ToDo
%{_docdir}/%{name}-%{version}/sample
%{_docdir}/%{name}-%{version}/ProgrammingRuby*


%files devel
%defattr(-, root, root)
%{_includedir}/*
%{_libdir}/libruby.so
%{_libdir}/libruby-static.a


%files tcltk
%defattr(-, root, root)
%{_libdir}/ruby/%{subver}/tcltk*
%{_libdir}/ruby/%{subver}/tk*
%{_libdir}/ruby/1.9/*/tcltklib.so
%{_libdir}/ruby/1.9/*/tkutil.so



%changelog
* Sun Mar 20 2011 Arkady L. Shane <ashejn@yandex-team.ru> - 1.9.1.p180-1
- update to 1.9.2 p180

* Thu Sep  2 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 1.9.1.p378-0.1
- rebuilt for Fedora

* Tue Jan 19 2010 Funda Wang <fwang@mandriva.org> 1.9.1.p378-3mdv2010.1
+ Revision: 493706
- provides ruby1.9

* Sun Jan 17 2010 Funda Wang <fwang@mandriva.org> 1.9.1.p378-1mdv2010.1
+ Revision: 492590
- update file list
- use progsuffix
- rediff old search path patch
- add 1.9.1 tarball
- add sources from ruby1.8
- Created package structure for ruby1.9.

