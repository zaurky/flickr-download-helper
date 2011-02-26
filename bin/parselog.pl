#!/usr/bin/perl
use strict;
use warnings;

use Text::Reform;
use utf8;

binmode STDOUT, ':utf8';

my $username = '';
my $date = '';
my $message = '';

my $format = "| [[[[[[[[[[[[[[[[[[[[[[[ | ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]] | [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[ |";
my %h_id2username = ();

while (<>) {
    binmode ARGV, ':utf8';
    if (/WARNING username/) {
        chomp;
        my @a = split('WARNING', $_);
        $a[1] =~ s/.* = //;
        $username = $a[1];
        $date = $a[0];
    } elsif (/WARNING (\d{6}):\tusername/) {
        my $id = $1;
        chomp;
        my @a = split('WARNING', $_);
        $a[1] =~ s/.* = //;
        $username = $a[1];
        $date = $a[0];
        $h_id2username{$id} = [$username, $date];
    } elsif (/(INFO|WARNING) download/) {
        chomp;
        s/.*(INFO|WARNING)//;
        if ($username ne '' and !/ 0 /) {
            print form $format, $date, $username, $_;
        }
    } elsif (/(INFO|WARNING) (\d{6}):\tdownload/) {
        my $id = $2;
        chomp;
        s/.*(INFO|WARNING) (\d{6}):\t//;

        if (defined $h_id2username{$id} and !/ 0 /) {
            print form $format, $h_id2username{$id}[1], $h_id2username{$id}[0], $_;
        }
    }
}

